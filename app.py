"""
Judicial Case Management System - Main Application
Flask backend with complete functionality
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import execute_query, execute_single

from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") 

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.route('/')
def index():
    """Landing page - redirect to login"""
    if 'user_id' in session:
        if session.get('user_type') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('judge_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for both Admin and Judge"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('user_type')  # 'admin' or 'judge'
        
        if user_type == 'admin':
            # Check admin credentials
            query = "SELECT * FROM Admin WHERE username = %s"
            user = execute_single(query, (username,))
            
            if user and user['password'] == password:  # In production, use hashed passwords
                session['user_id'] = user['admin_id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['user_type'] = 'admin'
                flash('Login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials!', 'error')
        
        elif user_type == 'judge':
            # Check judge credentials
            query = "SELECT * FROM Judge WHERE username = %s AND status = 'Active'"
            user = execute_single(query, (username,))
            
            if user and user['password'] == password:  # In production, use hashed passwords
                session['user_id'] = user['judge_id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['user_type'] = 'judge'
                flash('Login successful!', 'success')
                return redirect(url_for('judge_dashboard'))
            else:
                flash('Invalid judge credentials or account inactive!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ============================================
# ADMIN DASHBOARD & ROUTES
# ============================================

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard with statistics"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        flash('Please login as admin!', 'error')
        return redirect(url_for('login'))
    
    # Get dashboard statistics
    stats_query = """
    SELECT 
        (SELECT COUNT(*) FROM Judge WHERE status = 'Active') AS total_judges,
        (SELECT COUNT(*) FROM `Case`) AS total_cases,
        (SELECT COUNT(*) FROM `Case` WHERE status = 'Pending') AS pending_cases,
        (SELECT COUNT(*) FROM `Case` WHERE status = 'Heard') AS heard_cases,
        (SELECT COUNT(*) FROM `Case` WHERE status = 'Under Review') AS under_review_cases,
        (SELECT COUNT(*) FROM `Case` WHERE status = 'Closed') AS closed_cases,
        (SELECT COUNT(*) FROM `Case` WHERE status = 'Dismissed') AS dismissed_cases,
        (SELECT COUNT(*) FROM Hearing WHERE hearing_date = CURDATE() AND status = 'Scheduled') AS hearings_today,
        (SELECT COUNT(*) FROM Hearing WHERE hearing_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY) AND status = 'Scheduled') AS upcoming_hearings
    """
    stats = execute_single(stats_query)
    
    # Get case type distribution
    case_types_query = "SELECT case_type, COUNT(*) as count FROM `Case` GROUP BY case_type"
    case_types = execute_query(case_types_query, fetch=True)
    
    # Get recent cases
    recent_cases_query = """
    SELECT case_id, case_number, case_title, filing_date, status 
    FROM `Case` 
    ORDER BY filing_date DESC 
    LIMIT 5
    """
    recent_cases = execute_query(recent_cases_query, fetch=True)
    
    return render_template('admin_dashboard.html', 
                         stats=stats, 
                         case_types=case_types,
                         recent_cases=recent_cases)

@app.route('/admin/add-judge', methods=['GET', 'POST'])
def add_judge():
    """Add new judge"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        flash('Please login as admin!', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        specialization = request.form.get('specialization')
        experience_years = request.form.get('experience_years')
        
        # Insert judge into database
        query = """
        INSERT INTO Judge 
        (username, password, full_name, email, phone, specialization, 
         experience_years, assigned_by_admin_id, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Active', NOW())
        """
        params = (username, password, full_name, email, phone, 
                 specialization, experience_years, session['user_id'])
        
        result = execute_query(query, params)
        
        if result:
            flash(f'Judge {full_name} added successfully!', 'success')
            return redirect(url_for('view_judges'))
        else:
            flash('Error adding judge. Username or email might already exist.', 'error')
    
    return render_template('add_judge.html')

@app.route('/admin/judges')
def view_judges():
    """View all judges"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        flash('Please login as admin!', 'error')
        return redirect(url_for('login'))
    
    query = """
    SELECT j.*, 
           COUNT(c.case_id) as case_count 
    FROM Judge j
    LEFT JOIN `Case` c ON j.judge_id = c.assigned_judge_id
    GROUP BY j.judge_id
    ORDER BY j.created_at DESC
    """
    judges = execute_query(query, fetch=True)
    
    return render_template('view_judges.html', judges=judges)

@app.route('/admin/add-case', methods=['GET', 'POST'])
def add_case():
    """Add new case"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        flash('Please login as admin!', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        case_number = request.form.get('case_number')
        case_title = request.form.get('case_title')
        case_type = request.form.get('case_type')
        description = request.form.get('description')
        plaintiff_name = request.form.get('plaintiff_name')
        defendant_name = request.form.get('defendant_name')
        filing_date = request.form.get('filing_date')
        priority = request.form.get('priority')
        assigned_judge_id = request.form.get('assigned_judge_id')
        
        # Handle file upload
        pdf_path = None
        if 'pdf_file' in request.files:
            file = request.files['pdf_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{case_number.replace('/', '_')}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                pdf_path = f'uploads/{filename}'
        
        # Insert case into database
        query = """
        INSERT INTO `Case` 
        (case_number, case_title, case_type, description, plaintiff_name, 
         defendant_name, filing_date, status, priority, assigned_judge_id, 
         created_by_admin_id, pdf_document_path, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending', %s, %s, %s, %s, NOW(), NOW())
        """
        params = (case_number, case_title, case_type, description, plaintiff_name,
                 defendant_name, filing_date, priority, assigned_judge_id or None,
                 session['user_id'], pdf_path)
        
        result = execute_query(query, params)
        
        if result:
            flash(f'Case {case_number} added successfully!', 'success')
            return redirect(url_for('view_cases'))
        else:
            flash('Error adding case. Case number might already exist.', 'error')
    
    # Get active judges for dropdown
    judges_query = "SELECT judge_id, full_name, specialization FROM Judge WHERE status = 'Active' ORDER BY full_name"
    judges = execute_query(judges_query, fetch=True)
    
    return render_template('add_case.html', judges=judges)

@app.route('/admin/cases')
def view_cases():
    """View all cases"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        flash('Please login as admin!', 'error')
        return redirect(url_for('login'))
    
    query = """
    SELECT c.*, j.full_name as judge_name 
    FROM `Case` c
    LEFT JOIN Judge j ON c.assigned_judge_id = j.judge_id
    ORDER BY c.filing_date DESC
    """
    cases = execute_query(query, fetch=True)
    
    return render_template('view_cases.html', cases=cases, user_type='admin')

@app.route('/admin/case/<int:case_id>')
def admin_case_details(case_id):
    """View case details"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        flash('Please login as admin!', 'error')
        return redirect(url_for('login'))
    
    # Get case details
    case_query = """
    SELECT c.*, j.full_name as judge_name, j.specialization,
           a.full_name as created_by
    FROM `Case` c
    LEFT JOIN Judge j ON c.assigned_judge_id = j.judge_id
    LEFT JOIN Admin a ON c.created_by_admin_id = a.admin_id
    WHERE c.case_id = %s
    """
    case = execute_single(case_query, (case_id,))
    
    if not case:
        flash('Case not found!', 'error')
        return redirect(url_for('view_cases'))
    
    # Get hearings for this case
    hearings_query = """
    SELECT h.*, a.full_name as scheduled_by
    FROM Hearing h
    LEFT JOIN Admin a ON h.scheduled_by_admin_id = a.admin_id
    WHERE h.case_id = %s
    ORDER BY h.hearing_date DESC, h.hearing_time DESC
    """
    hearings = execute_query(hearings_query, (case_id,), fetch=True)
    
    return render_template('case_details.html', case=case, hearings=hearings, user_type='admin')

@app.route('/admin/schedule-hearing/<int:case_id>', methods=['GET', 'POST'])
def schedule_hearing(case_id):
    """Schedule a hearing for a case"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        flash('Please login as admin!', 'error')
        return redirect(url_for('login'))
    
    # Get case details
    case = execute_single("SELECT * FROM `Case` WHERE case_id = %s", (case_id,))
    
    if not case:
        flash('Case not found!', 'error')
        return redirect(url_for('view_cases'))
    
    if request.method == 'POST':
        hearing_date = request.form.get('hearing_date')
        hearing_time = request.form.get('hearing_time')
        courtroom_number = request.form.get('courtroom_number')
        hearing_type = request.form.get('hearing_type')
        notes = request.form.get('notes')
        
        query = """
        INSERT INTO Hearing 
        (case_id, hearing_date, hearing_time, courtroom_number, hearing_type, 
         status, notes, scheduled_by_admin_id, created_at)
        VALUES (%s, %s, %s, %s, %s, 'Scheduled', %s, %s, NOW())
        """
        params = (case_id, hearing_date, hearing_time, courtroom_number, 
                 hearing_type, notes, session['user_id'])
        
        result = execute_query(query, params)
        
        if result:
            flash('Hearing scheduled successfully!', 'success')
            return redirect(url_for('admin_case_details', case_id=case_id))
        else:
            flash('Error scheduling hearing.', 'error')
    
    return render_template('schedule_hearing.html', case=case)

@app.route('/admin/search-case')
def admin_search_case():
    """Search case by case_id or case_number"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    search_term = request.args.get('q', '')
    
    if not search_term:
        return jsonify({'error': 'Search term required'}), 400
    
    # Search by case_id or case_number
    query = """
    SELECT c.*, j.full_name as judge_name 
    FROM `Case` c
    LEFT JOIN Judge j ON c.assigned_judge_id = j.judge_id
    WHERE c.case_id = %s OR c.case_number LIKE %s
    LIMIT 10
    """
    
    # Try to convert to int for case_id search
    try:
        case_id = int(search_term)
    except ValueError:
        case_id = -1
    
    results = execute_query(query, (case_id, f'%{search_term}%'), fetch=True)
    
    return jsonify(results or [])

# ============================================
# JUDGE DASHBOARD & ROUTES
# ============================================

@app.route('/judge/dashboard')
def judge_dashboard():
    """Judge dashboard showing assigned cases"""
    if 'user_id' not in session or session.get('user_type') != 'judge':
        flash('Please login as judge!', 'error')
        return redirect(url_for('login'))
    
    judge_id = session['user_id']
    
    # Get judge's assigned cases statistics
    stats_query = """
    SELECT 
        COUNT(*) AS total_assigned,
        SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending,
        SUM(CASE WHEN status = 'Heard' THEN 1 ELSE 0 END) AS heard,
        SUM(CASE WHEN status = 'Under Review' THEN 1 ELSE 0 END) AS under_review,
        SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) AS closed
    FROM `Case`
    WHERE assigned_judge_id = %s
    """
    stats = execute_single(stats_query, (judge_id,))
    
    # Get upcoming hearings
    hearings_query = """
    SELECT h.*, c.case_number, c.case_title
    FROM Hearing h
    JOIN `Case` c ON h.case_id = c.case_id
    WHERE c.assigned_judge_id = %s 
    AND h.hearing_date >= CURDATE()
    AND h.status = 'Scheduled'
    ORDER BY h.hearing_date, h.hearing_time
    LIMIT 5
    """
    upcoming_hearings = execute_query(hearings_query, (judge_id,), fetch=True)
    
    # Get recent assigned cases
    recent_cases_query = """
    SELECT case_id, case_number, case_title, case_type, filing_date, status, priority
    FROM `Case`
    WHERE assigned_judge_id = %s
    ORDER BY filing_date DESC
    LIMIT 5
    """
    recent_cases = execute_query(recent_cases_query, (judge_id,), fetch=True)
    
    return render_template('judge_dashboard.html', 
                         stats=stats,
                         upcoming_hearings=upcoming_hearings,
                         recent_cases=recent_cases)

@app.route('/judge/my-cases')
def judge_my_cases():
    """View all cases assigned to logged-in judge"""
    if 'user_id' not in session or session.get('user_type') != 'judge':
        flash('Please login as judge!', 'error')
        return redirect(url_for('login'))
    
    judge_id = session['user_id']
    
    query = """
    SELECT c.* 
    FROM `Case` c
    WHERE c.assigned_judge_id = %s
    ORDER BY c.filing_date DESC
    """
    cases = execute_query(query, (judge_id,), fetch=True)
    
    return render_template('judge_cases.html', cases=cases)

@app.route('/judge/case/<int:case_id>')
def judge_case_details(case_id):
    """View case details for judge"""
    if 'user_id' not in session or session.get('user_type') != 'judge':
        flash('Please login as judge!', 'error')
        return redirect(url_for('login'))
    
    judge_id = session['user_id']
    
    # Verify this case is assigned to this judge
    case_query = """
    SELECT c.*, a.full_name as created_by
    FROM `Case` c
    LEFT JOIN Admin a ON c.created_by_admin_id = a.admin_id
    WHERE c.case_id = %s AND c.assigned_judge_id = %s
    """
    case = execute_single(case_query, (case_id, judge_id))
    
    if not case:
        flash('Case not found or not assigned to you!', 'error')
        return redirect(url_for('judge_my_cases'))
    
    # Get hearings for this case
    hearings_query = """
    SELECT h.*, a.full_name as scheduled_by
    FROM Hearing h
    LEFT JOIN Admin a ON h.scheduled_by_admin_id = a.admin_id
    WHERE h.case_id = %s
    ORDER BY h.hearing_date DESC, h.hearing_time DESC
    """
    hearings = execute_query(hearings_query, (case_id,), fetch=True)
    
    return render_template('case_details.html', case=case, hearings=hearings, user_type='judge')

@app.route('/judge/search-by-id')
def judge_search_by_judge_id():
    """Search cases assigned to a specific judge by judge_id"""
    if 'user_id' not in session or session.get('user_type') != 'judge':
        return jsonify({'error': 'Unauthorized'}), 401
    
    judge_id = request.args.get('judge_id', '')
    
    if not judge_id:
        return jsonify({'error': 'Judge ID required'}), 400
    
    query = """
    SELECT c.*, j.full_name as judge_name 
    FROM `Case` c
    LEFT JOIN Judge j ON c.assigned_judge_id = j.judge_id
    WHERE c.assigned_judge_id = %s
    ORDER BY c.filing_date DESC
    """
    
    results = execute_query(query, (judge_id,), fetch=True)
    
    return jsonify(results or [])

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/dashboard-stats')
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    stats_query = """
    SELECT 
        (SELECT COUNT(*) FROM Judge WHERE status = 'Active') AS total_judges,
        (SELECT COUNT(*) FROM `Case`) AS total_cases,
        (SELECT COUNT(*) FROM `Case` WHERE status = 'Pending') AS pending_cases,
        (SELECT COUNT(*) FROM `Case` WHERE status = 'Heard') AS heard_cases,
        (SELECT COUNT(*) FROM `Case` WHERE status = 'Under Review') AS under_review_cases,
        (SELECT COUNT(*) FROM `Case` WHERE status = 'Closed') AS closed_cases,
        (SELECT COUNT(*) FROM `Case` WHERE status = 'Dismissed') AS dismissed_cases,
        (SELECT COUNT(*) FROM Hearing WHERE hearing_date = CURDATE() AND status = 'Scheduled') AS hearings_today,
        (SELECT COUNT(*) FROM Hearing WHERE hearing_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY) AND status = 'Scheduled') AS upcoming_hearings
    """
    stats = execute_single(stats_query)
    
    return jsonify(stats)

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# ============================================
# RUN APPLICATION
# ============================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)