CREATE DATABASE IF NOT EXISTS judicial_case_management;
USE judicial_case_management;
-- MILESSTONE 4 OF CREATING TABLES
-- TABLE 1: ADMIN
CREATE TABLE Admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- TABLE 2: JUDGE
CREATE TABLE Judge (
    judge_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    specialization VARCHAR(50),
    experience_years INT,
    assigned_by_admin_id INT,
    status ENUM('Active', 'Inactive', 'On Leave') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraint
    CONSTRAINT fk_judge_admin 
        FOREIGN KEY (assigned_by_admin_id) 
        REFERENCES Admin(admin_id) 
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    
    -- Indexes for performance
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_specialization (specialization),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- TABLE 3: CASE
CREATE TABLE `Case` (
    case_id INT AUTO_INCREMENT PRIMARY KEY,
    case_number VARCHAR(50) UNIQUE NOT NULL,
    case_title VARCHAR(200) NOT NULL,
    case_type ENUM('Criminal', 'Civil', 'Family', 'Corporate', 'Other') NOT NULL,
    description TEXT,
    plaintiff_name VARCHAR(100) NOT NULL,
    defendant_name VARCHAR(100) NOT NULL,
    filing_date DATE NOT NULL,
    status ENUM('Pending', 'Heard', 'Under Review', 'Closed', 'Dismissed') DEFAULT 'Pending',
    priority ENUM('High', 'Medium', 'Low') DEFAULT 'Medium',
    assigned_judge_id INT,
    created_by_admin_id INT,
    pdf_document_path VARCHAR(255),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    CONSTRAINT fk_case_judge 
        FOREIGN KEY (assigned_judge_id) 
        REFERENCES Judge(judge_id) 
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_case_admin 
        FOREIGN KEY (created_by_admin_id) 
        REFERENCES Admin(admin_id) 
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    
    -- Indexes for performance
    INDEX idx_case_number (case_number),
    INDEX idx_case_type (case_type),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_filing_date (filing_date),
    INDEX idx_assigned_judge (assigned_judge_id),
    INDEX idx_created_by_admin (created_by_admin_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- TABLE 4: HEARING
CREATE TABLE Hearing (
    hearing_id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    hearing_date DATE NOT NULL,
    hearing_time TIME NOT NULL,
    courtroom_number VARCHAR(20),
    hearing_type ENUM('Initial', 'Follow-up', 'Final', 'Evidence', 'Verdict') NOT NULL,
    status ENUM('Scheduled', 'Completed', 'Postponed', 'Cancelled') DEFAULT 'Scheduled',
    notes TEXT,
    next_hearing_date DATE,
    scheduled_by_admin_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    CONSTRAINT fk_hearing_case 
        FOREIGN KEY (case_id) 
        REFERENCES `Case`(case_id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_hearing_admin 
        FOREIGN KEY (scheduled_by_admin_id) 
        REFERENCES Admin(admin_id) 
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    
    -- Indexes for performance
    INDEX idx_case_id (case_id),
    INDEX idx_hearing_date (hearing_date),
    INDEX idx_hearing_type (hearing_type),
    INDEX idx_status (status),
    INDEX idx_scheduled_by (scheduled_by_admin_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
SHOW COLUMNS FROM ADMIN;
SHOW COLUMNS FROM HEARING;
SHOW COLUMNS FROM JUDGE;
SHOW COLUMNS FROM `Case`;

SELECT 'Admin' AS Table_Name, COUNT(*) AS Record_Count FROM Admin
UNION ALL
SELECT 'Judge', COUNT(*) FROM Judge
UNION ALL
SELECT 'Case', COUNT(*) FROM `Case`
UNION ALL
SELECT 'Hearing', COUNT(*) FROM Hearing;
SELECT * FROM Hearing;
SELECT * FROM `Case`;
-- Disable foreign key checks first
SET FOREIGN_KEY_CHECKS = 0;

-- Truncate all tables (deletes all data, resets AUTO_INCREMENT)
TRUNCATE TABLE Hearing;
TRUNCATE TABLE `Case`;
TRUNCATE TABLE Judge;
TRUNCATE TABLE Admin;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;
-- MILESTONE 5 FOR CHECKING LOADED DATA
select * from hearing;
select * from `Case`;
select * from judge;
SELECT * FROM ADMIN;



