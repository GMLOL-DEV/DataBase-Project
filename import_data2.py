from faker import Faker
import random
import mysql.connector
from datetime import datetime, timedelta

fake = Faker()

# =========================================
# DATABASE CONNECTION
# =========================================

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Pakistankpk@1',
    database='judicial_case_management'
)

cursor = conn.cursor()

print("Connected Successfully")


# =========================================
# CONFIG
# =========================================

TOTAL_ADMINS = 5
TOTAL_JUDGES = 10
TOTAL_CASES = 100

PDF_BASE_PATH = r"C:\Users\HP\OneDrive\Desktop\judicial_project\pdf_paths\\"


# =========================================
# HELPER FUNCTIONS
# =========================================

def random_case_status():
    return random.choice([
        'Pending',
        'Heard',
        'Under Review',
        'Closed',
        'Dismissed'
    ])


def random_priority():
    return random.choice([
        'High',
        'Medium',
        'Low'
    ])


def random_case_type():
    return random.choice([
        'Criminal',
        'Civil',
        'Family',
        'Corporate',
        'Other'
    ])


def generate_case_description(case_type):

    descriptions = {

        'Criminal': [
            'The accused was charged with armed robbery after CCTV evidence and eyewitness testimony were presented before the court.',
            'The case involves illegal possession of narcotics during a highway security inspection.',
            'The plaintiff filed a criminal complaint regarding fraud and financial misappropriation.'
        ],

        'Civil': [
            'The plaintiff filed a civil suit regarding breach of contract and delayed payment obligations.',
            'The dispute concerns ownership rights of commercial property between two parties.',
            'The petitioner requested compensation for damages caused by construction negligence.'
        ],

        'Family': [
            'The petition concerns child custody and maintenance after marital separation.',
            'The matter involves inheritance distribution among legal heirs.',
            'The plaintiff requested legal guardianship rights for a minor child.'
        ],

        'Corporate': [
            'The company filed a lawsuit regarding unpaid invoices and breach of service agreement.',
            'The case concerns shareholder disputes and unauthorized financial transactions.',
            'The plaintiff reported violation of a software licensing agreement.'
        ],

        'Other': [
            'The petitioner requested judicial review regarding procedural irregularities.',
            'The dispute concerns regulatory compliance and administrative review.',
            'The matter was submitted before the court for legal clarification.'
        ]
    }

    return random.choice(descriptions[case_type])


# =========================================
# INSERT ADMINS
# =========================================

for _ in range(TOTAL_ADMINS):

    username = "admin_" + fake.unique.first_name().lower()

    password = "admin123"

    full_name = fake.name()

    email = fake.unique.email()

    phone = "03" + str(random.randint(100000000, 499999999))

    sql = """
    INSERT INTO Admin
    (username, password, full_name, email, phone)
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        username,
        password,
        full_name,
        email,
        phone
    )

    cursor.execute(sql, values)

conn.commit()

print("Admins Inserted")


# =========================================
# INSERT JUDGES
# =========================================

specializations = [
    'Criminal',
    'Civil',
    'Family',
    'Corporate'
]

judge_statuses = [
    'Active',
    'Inactive',
    'On Leave'
]

for _ in range(TOTAL_JUDGES):

    username = "judge_" + fake.unique.first_name().lower()

    password = "judge123"

    full_name = "Justice " + fake.name()

    email = fake.unique.email()

    phone = "03" + str(random.randint(100000000, 499999999))

    specialization = random.choice(specializations)

    experience_years = random.randint(5, 30)

    assigned_admin = random.randint(1, TOTAL_ADMINS)

    status = random.choice(judge_statuses)

    sql = """
    INSERT INTO Judge
    (
        username,
        password,
        full_name,
        email,
        phone,
        specialization,
        experience_years,
        assigned_by_admin_id,
        status
    )

    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        username,
        password,
        full_name,
        email,
        phone,
        specialization,
        experience_years,
        assigned_admin,
        status
    )

    cursor.execute(sql, values)

conn.commit()

print("Judges Inserted")


# =========================================
# INSERT CASES + HEARINGS
# =========================================

for i in range(1, TOTAL_CASES + 1):

    case_type = random_case_type()

    year = random.randint(2024, 2026)

    prefix = case_type[:2].upper()

    case_number = f"{prefix}-{year}-{str(i).zfill(4)}"

    case_title = f"{fake.last_name()} vs {fake.last_name()}"

    description = generate_case_description(case_type)

    plaintiff_name = fake.name()

    defendant_name = fake.name()

    filing_start = datetime.now() - timedelta(days=730)

    filing_end = datetime.now() - timedelta(days=30)

    filing_date = fake.date_between_dates(
        date_start=filing_start,
        date_end=filing_end
    )

    status = random_case_status()

    priority = random_priority()

    judge_id = random.randint(1, TOTAL_JUDGES)

    admin_id = random.randint(1, TOTAL_ADMINS)

    pdf_path = PDF_BASE_PATH + case_number + ".pdf"

    remarks = fake.sentence(nb_words=10)

    sql = """
    INSERT INTO `Case`
    (
        case_number,
        case_title,
        case_type,
        description,
        plaintiff_name,
        defendant_name,
        filing_date,
        status,
        priority,
        assigned_judge_id,
        created_by_admin_id,
        pdf_document_path,
        remarks
    )

    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        case_number,
        case_title,
        case_type,
        description,
        plaintiff_name,
        defendant_name,
        filing_date,
        status,
        priority,
        judge_id,
        admin_id,
        pdf_path,
        remarks
    )

    cursor.execute(sql, values)

    case_id = cursor.lastrowid


    # =========================================
    # HEARING DATA
    # =========================================

    hearing_types = [
        'Initial',
        'Follow-up',
        'Final',
        'Evidence',
        'Verdict'
    ]

    hearing_type = random.choice(hearing_types)

    courtroom = f"Courtroom-{chr(random.randint(65, 70))}-{random.randint(1, 10)}"

    hearing_time = f"{random.randint(9,15)}:{str(random.randint(0,59)).zfill(2)}:00"


    # =========================================
    # STATUS-BASED HEARING LOGIC
    # =========================================

    if status in ['Pending', 'Under Review']:

        hearing_status = 'Scheduled'

        hearing_date = fake.date_between_dates(
            date_start=datetime.now(),
            date_end=datetime.now() + timedelta(days=30)
        )

        next_hearing_date = fake.date_between_dates(
            date_start=datetime.now() + timedelta(days=31),
            date_end=datetime.now() + timedelta(days=60)
        )


    elif status == 'Heard':

        hearing_status = 'Completed'

        hearing_date = fake.date_between_dates(
            date_start=datetime.now() - timedelta(days=30),
            date_end=datetime.now() - timedelta(days=1)
        )

        next_hearing_date = None


    elif status == 'Closed':

        hearing_status = 'Completed'

        hearing_type = 'Verdict'

        hearing_date = fake.date_between_dates(
            date_start=datetime.now() - timedelta(days=180),
            date_end=datetime.now() - timedelta(days=30)
        )

        next_hearing_date = None


    else:

        # Dismissed

        hearing_status = 'Cancelled'

        hearing_date = fake.date_between_dates(
            date_start=datetime.now() - timedelta(days=90),
            date_end=datetime.now() - timedelta(days=10)
        )

        next_hearing_date = None


    notes = fake.paragraph()

    sql = """
    INSERT INTO Hearing
    (
        case_id,
        hearing_date,
        hearing_time,
        courtroom_number,
        hearing_type,
        status,
        notes,
        next_hearing_date,
        scheduled_by_admin_id
    )

    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        case_id,
        hearing_date,
        hearing_time,
        courtroom,
        hearing_type,
        hearing_status,
        notes,
        next_hearing_date,
        admin_id
    )

    cursor.execute(sql, values)

conn.commit()

print("Cases + Hearings Inserted Successfully")

cursor.close()
conn.close()

print("Database Connection Closed")