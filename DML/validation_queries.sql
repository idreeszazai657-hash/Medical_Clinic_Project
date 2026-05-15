USE medical_clinic;

-- ==========================================
-- 1. DATA MODIFICATION DEMONSTRATION
-- ==========================================

-- Demonstrating an UPDATE operation with a WHERE condition
-- Updating the status of a specific bill to 'Paid'
UPDATE BILLS 
SET status = 'Paid' 
WHERE bill_id = 5 AND status = 'Unpaid';

-- Demonstrating a DELETE operation with a WHERE condition
-- Deleting a specific old visit (Since we have ON DELETE CASCADE, this will safely remove linked records in VISIT_SERVICES and PRESCRIPTIONS)
DELETE FROM VISITS 
WHERE visit_id = 60;

-- ==========================================
-- 2. VALIDATION QUERIES
-- ==========================================

-- A. COUNT(*) for each table to confirm row counts
SELECT 'USERS' AS Table_Name, COUNT(*) AS Row_Count FROM USERS
UNION ALL
SELECT 'PATIENTS', COUNT(*) FROM PATIENTS
UNION ALL
SELECT 'DOCTORS', COUNT(*) FROM DOCTORS
UNION ALL
SELECT 'MEDICAL_SERVICES', COUNT(*) FROM MEDICAL_SERVICES
UNION ALL
SELECT 'VISITS', COUNT(*) FROM VISITS
UNION ALL
SELECT 'PRESCRIPTIONS', COUNT(*) FROM PRESCRIPTIONS
UNION ALL
SELECT 'VISIT_SERVICES', COUNT(*) FROM VISIT_SERVICES
UNION ALL
SELECT 'BILLS', COUNT(*) FROM BILLS;


-- B. NULL check on key columns
-- This should return 0 rows if our NOT NULL constraints and data population worked correctly
SELECT 'Missing Patient Name' AS Issue_Type, COUNT(*) AS Count FROM PATIENTS WHERE first_name IS NULL
UNION ALL
SELECT 'Missing Visit Date', COUNT(*) FROM VISITS WHERE visit_date IS NULL
UNION ALL
SELECT 'Missing Bill Total', COUNT(*) FROM BILLS WHERE total_amount IS NULL;


-- C. JOIN-based check to confirm foreign key integrity
-- This checks if there are any VISITS assigned to a patient_id that DOES NOT exist in the PATIENTS table.
-- Because of our Foreign Key constraints, this MUST return 0 rows.
SELECT 
    v.visit_id, 
    v.patient_id AS Orphaned_Patient_ID 
FROM 
    VISITS v
LEFT JOIN 
    PATIENTS p ON v.patient_id = p.patient_id
WHERE 
    p.patient_id IS NULL;
