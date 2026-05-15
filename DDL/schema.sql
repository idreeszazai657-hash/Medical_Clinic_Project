CREATE DATABASE IF NOT EXISTS medical_clinic;
USE medical_clinic;

-- 1. USERS Table
CREATE TABLE USERS (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('Admin', 'Receptionist')),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL
);

-- 2. PATIENTS Table
CREATE TABLE PATIENTS (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    dob DATE NOT NULL,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    contact VARCHAR(20) NOT NULL
);

-- 3. DOCTORS Table
CREATE TABLE DOCTORS (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    contact VARCHAR(20) NOT NULL,
    room_number VARCHAR(20) NOT NULL
);

-- 4. MEDICAL_SERVICES Table
CREATE TABLE MEDICAL_SERVICES (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0)
);

-- 5. VISITS Table
CREATE TABLE VISITS (
    visit_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    visit_date DATETIME NOT NULL,
    diagnosis TEXT,
    FOREIGN KEY (patient_id) REFERENCES PATIENTS(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES DOCTORS(doctor_id) ON DELETE CASCADE
);

-- 6. PRESCRIPTIONS Table
CREATE TABLE PRESCRIPTIONS (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    visit_id INT NOT NULL,
    medicine_name VARCHAR(100) NOT NULL,
    dosage VARCHAR(50) NOT NULL,
    instructions TEXT,
    FOREIGN KEY (visit_id) REFERENCES VISITS(visit_id) ON DELETE CASCADE
);

-- 7. VISIT_SERVICES Table
CREATE TABLE VISIT_SERVICES (
    vs_id INT AUTO_INCREMENT PRIMARY KEY,
    visit_id INT NOT NULL,
    service_id INT NOT NULL,
    FOREIGN KEY (visit_id) REFERENCES VISITS(visit_id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES MEDICAL_SERVICES(service_id) ON DELETE CASCADE
);

-- 8. BILLS Table
CREATE TABLE BILLS (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    visit_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    status VARCHAR(20) NOT NULL CHECK (status IN ('Paid', 'Unpaid')),
    FOREIGN KEY (visit_id) REFERENCES VISITS(visit_id) ON DELETE CASCADE
);

-- ==========================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ==========================================

-- Indexes on Foreign Keys (MySQL automatically creates indexes on FKs, but being explicit is good practice)
CREATE INDEX idx_visits_patient_id ON VISITS(patient_id);
CREATE INDEX idx_visits_doctor_id ON VISITS(doctor_id);
CREATE INDEX idx_prescriptions_visit_id ON PRESCRIPTIONS(visit_id);
CREATE INDEX idx_visit_services_visit_id ON VISIT_SERVICES(visit_id);
CREATE INDEX idx_visit_services_service_id ON VISIT_SERVICES(service_id);
CREATE INDEX idx_bills_visit_id ON BILLS(visit_id);

-- Additional Indexes on Frequently Queried Columns
CREATE INDEX idx_patients_last_name ON PATIENTS(last_name);
CREATE INDEX idx_doctors_specialty ON DOCTORS(specialty);
CREATE INDEX idx_visits_date ON VISITS(visit_date);
