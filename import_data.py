"""
Import CSV Data into MySQL Database
This script imports all CSV files into the judicial_case_management database
"""

import mysql.connector
import csv
from mysql.connector import Error

# ============================================
# DATABASE CONFIGURATION
# ============================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',           # Change to your MySQL username
    'password': 'Pakistankpk@1',  # Change to your MySQL password
    'database': 'judicial_case_management'
}

def create_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("✓ Connected to MySQL database")
        return connection
    except Error as e:
        print(f"✗ Error connecting to database: {e}")
        return None

def import_admin_data(connection, csv_file):
    """Import Admin data from CSV"""
    cursor = connection.cursor()
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            
            for row in csv_reader:
                query = """
                INSERT INTO Admin 
                (admin_id, username, password, full_name, email, phone, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    row['admin_id'],
                    row['username'],
                    row['password'],
                    row['full_name'],
                    row['email'],
                    row['phone'],
                    row['created_at']
                )
                cursor.execute(query, values)
        
        connection.commit()
        print(f"✓ Imported {cursor.rowcount} admin records")
        
    except Error as e:
        print(f"✗ Error importing admin data: {e}")
        connection.rollback()
    finally:
        cursor.close()

def import_judge_data(connection, csv_file):
    """Import Judge data from CSV"""
    cursor = connection.cursor()
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            
            count = 0
            for row in csv_reader:
                query = """
                INSERT INTO Judge 
                (judge_id, username, password, full_name, email, phone, 
                 specialization, experience_years, assigned_by_admin_id, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    row['judge_id'],
                    row['username'],
                    row['password'],
                    row['full_name'],
                    row['email'],
                    row['phone'],
                    row['specialization'],
                    row['experience_years'],
                    row['assigned_by_admin_id'],
                    row['status'],
                    row['created_at']
                )
                cursor.execute(query, values)
                count += 1
        
        connection.commit()
        print(f"✓ Imported {count} judge records")
        
    except Error as e:
        print(f"✗ Error importing judge data: {e}")
        connection.rollback()
    finally:
        cursor.close()

def import_case_data(connection, csv_file):
    """Import Case data from CSV"""
    cursor = connection.cursor()
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            
            count = 0
            for row in csv_reader:
                query = """
                INSERT INTO `Case` 
                (case_id, case_number, case_title, case_type, description, 
                 plaintiff_name, defendant_name, filing_date, status, priority, 
                 assigned_judge_id, created_by_admin_id, pdf_document_path, 
                 remarks, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Handle NULL values for assigned_judge_id
                assigned_judge = row['assigned_judge_id'] if row['assigned_judge_id'] else None
                
                values = (
                    row['case_id'],
                    row['case_number'],
                    row['case_title'],
                    row['case_type'],
                    row['description'],
                    row['plaintiff_name'],
                    row['defendant_name'],
                    row['filing_date'],
                    row['status'],
                    row['priority'],
                    assigned_judge,
                    row['created_by_admin_id'],
                    row['pdf_document_path'],
                    row['remarks'],
                    row['created_at'],
                    row['updated_at']
                )
                cursor.execute(query, values)
                count += 1
        
        connection.commit()
        print(f"✓ Imported {count} case records")
        
    except Error as e:
        print(f"✗ Error importing case data: {e}")
        connection.rollback()
    finally:
        cursor.close()

def import_hearing_data(connection, csv_file):
    """Import Hearing data from CSV"""
    cursor = connection.cursor()
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            
            count = 0
            for row in csv_reader:
                query = """
                INSERT INTO Hearing 
                (hearing_id, case_id, hearing_date, hearing_time, courtroom_number, 
                 hearing_type, status, notes, next_hearing_date, scheduled_by_admin_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Handle NULL values for next_hearing_date
                next_hearing = row['next_hearing_date'] if row['next_hearing_date'] else None
                
                values = (
                    row['hearing_id'],
                    row['case_id'],
                    row['hearing_date'],
                    row['hearing_time'],
                    row['courtroom_number'],
                    row['hearing_type'],
                    row['status'],
                    row['notes'],
                    next_hearing,
                    row['scheduled_by_admin_id'],
                    row['created_at']
                )
                cursor.execute(query, values)
                count += 1
        
        connection.commit()
        print(f"✓ Imported {count} hearing records")
        
    except Error as e:
        print(f"✗ Error importing hearing data: {e}")
        connection.rollback()
    finally:
        cursor.close()

def verify_import(connection):
    """Verify data was imported correctly"""
    cursor = connection.cursor()
    
    print("\n" + "="*50)
    print("IMPORT VERIFICATION")
    print("="*50)
    
    tables = ['Admin', 'Judge', '`Case`', 'Hearing']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table.strip('`')}: {count} records")
    
    cursor.close()
    print("="*50)

def main():
    """Main import function"""
    print("="*50)
    print("JUDICIAL CASE MANAGEMENT SYSTEM")
    print("CSV Data Import Tool")
    print("="*50)
    print()
    
    # Create connection
    connection = create_connection()
    if not connection:
        return
    
    try:
        # Disable foreign key checks temporarily
        cursor = connection.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.close()
        
        # Import data in correct order (respecting foreign keys)
        print("\nImporting data...")
        import_admin_data(connection, 'admin_data.csv')
        import_judge_data(connection, 'judge_data.csv')
        import_case_data(connection, 'case_data.csv')
        import_hearing_data(connection, 'hearing_data.csv')
        
        # Re-enable foreign key checks
        cursor = connection.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        cursor.close()
        
        # Verify import
        verify_import(connection)
        
        print("\n✅ Data import completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
    
    finally:
        if connection.is_connected():
            connection.close()
            print("\n✓ Database connection closed")

if __name__ == "__main__":
    main()
