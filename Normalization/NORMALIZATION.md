# Normalization Document (Milestone 2)

This document formalizes the normalization process applied to the Medical Clinic Database schema to ensure data integrity and eliminate redundancy.

## Step 1 & 2 — Apply Normalization & Remove Duplicates

### 1NF (First Normal Form)
**Rule**: All attributes must be atomic (no multi-valued attributes), and each record must be unique.

*   **Issue Found**: 
    1. The `full_name` fields in `USERS`, `PATIENTS`, and `DOCTORS` were not atomic because they contained both the first and last names in a single string.
    2. The `prescribed_medicines` field in the `VISITS` table could contain multiple medicine names (e.g., "Paracetamol, Amoxicillin"), which violates the rule against multi-valued attributes.
*   **Changes Made**: 
    1. Split `full_name` into `first_name` and `last_name` across `USERS`, `PATIENTS`, and `DOCTORS`.
    2. Removed the `prescribed_medicines` column from `VISITS` and created a new separate table called `PRESCRIPTIONS` (`prescription_id`, `visit_id`, `medicine_name`, `dosage`, `instructions`).
*   **Why**: To comply with 1NF, every column must hold a single, indivisible value. Creating the `PRESCRIPTIONS` table allows a single visit to have multiple medicines without violating atomicity.

### 2NF (Second Normal Form)
**Rule**: Must be in 1NF, and every non-prime attribute must be fully functionally dependent on the entire primary key (no partial dependencies).

*   **Issue Found**: None. 
*   **Changes Made**: None.
*   **Why**: Partial dependencies only exist in tables that have a composite primary key. All of our tables use a single-column surrogate primary key (e.g., `patient_id`, `visit_id`, `prescription_id`). Since the primary keys consist of only a single attribute, it is impossible to have a partial dependency. Therefore, since the schema is in 1NF, it is automatically in 2NF.

### 3NF (Third Normal Form)
**Rule**: Must be in 2NF, and there must be no transitive dependencies (a non-prime attribute depending on another non-prime attribute).

*   **Issue Found**: None.
*   **Changes Made**: None.
*   **Why**: We reviewed all tables to ensure attributes depend only on the primary key. For example, in `PATIENTS`, attributes like `dob` and `gender` depend directly on `patient_id` and not on each other. In `BILLS`, while `total_amount` is related to the services provided in a visit, we explicitly store it to preserve a historical snapshot of the bill at the time it was generated (preventing past bills from changing if a medical service updates its price). Thus, there are no structural transitive dependencies that need to be resolved. The schema is successfully in 3NF.

## Step 3 — Updated ERD

The ER Diagram has been updated to reflect these normalization changes. 
*   The `PRESCRIPTIONS` entity was added and linked to `VISITS` (1-to-many relationship).
*   The `full_name` attributes in `USERS`, `PATIENTS`, and `DOCTORS` were replaced with `first_name` and `last_name`.

*(The updated ERD file `updated_erd_M2.png` is located in the `ERD` directory).*
