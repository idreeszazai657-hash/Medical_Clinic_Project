import csv
import random
from datetime import datetime, timedelta
import os

# Create Data directory if it doesn't exist
os.makedirs('Data', exist_ok=True)

# Helper data
first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Idrees", "Farman"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Zazai", "Afridi"]
specialties = ["Cardiology", "Dermatology", "Neurology", "Pediatrics", "Orthopedics", "General Practice", "Ophthalmology", "Psychiatry", "Oncology", "Radiology"]
medicines = ["Paracetamol", "Amoxicillin", "Ibuprofen", "Omeprazole", "Lisinopril", "Metformin", "Amlodipine", "Albuterol", "Gabapentin", "Losartan", "Atorvastatin"]
services = [("Consultation", 50.0), ("Blood Test", 25.0), ("X-Ray", 100.0), ("MRI Scan", 400.0), ("ECG", 75.0), ("Ultrasound", 150.0), ("Vaccination", 30.0), ("Physical Therapy", 80.0)]
diagnoses = ["Healthy", "Common Cold", "Flu", "Hypertension", "Migraine", "Sprained Ankle", "Asthma", "Diabetes Type 2", "Anemia", "Acid Reflux"]

# Number of records to generate
NUM_RECORDS = 60

# 1. USERS
with open('Data/USERS.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['user_id', 'username', 'password_hash', 'role', 'first_name', 'last_name'])
    for i in range(1, NUM_RECORDS + 1):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        role = "Admin" if i <= 5 else "Receptionist"
        writer.writerow([i, f"{fname.lower()}.{lname.lower()}{i}", f"hashed_pwd_{i}", role, fname, lname])

# 2. PATIENTS
with open('Data/PATIENTS.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['patient_id', 'first_name', 'last_name', 'dob', 'gender', 'contact'])
    for i in range(1, NUM_RECORDS + 1):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        start_date = datetime(1950, 1, 1)
        end_date = datetime(2015, 12, 31)
        random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        gender = random.choice(["Male", "Female"])
        contact = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        writer.writerow([i, fname, lname, random_date.strftime('%Y-%m-%d'), gender, contact])

# 3. DOCTORS
with open('Data/DOCTORS.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['doctor_id', 'first_name', 'last_name', 'specialty', 'contact', 'room_number'])
    for i in range(1, NUM_RECORDS + 1):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        specialty = random.choice(specialties)
        contact = f"555-DOC-{random.randint(1000, 9999)}"
        room = f"Room {random.randint(101, 399)}"
        writer.writerow([i, fname, lname, specialty, contact, room])

# 4. MEDICAL_SERVICES
with open('Data/MEDICAL_SERVICES.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['service_id', 'service_name', 'price'])
    # Add base services
    for i, (s_name, price) in enumerate(services, 1):
        writer.writerow([i, s_name, price])
    # Generate remaining up to NUM_RECORDS
    for i in range(len(services) + 1, NUM_RECORDS + 1):
        writer.writerow([i, f"Specialized Test {i}", round(random.uniform(50.0, 500.0), 2)])

# 5. VISITS
with open('Data/VISITS.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['visit_id', 'patient_id', 'doctor_id', 'visit_date', 'diagnosis'])
    for i in range(1, NUM_RECORDS + 1):
        patient_id = random.randint(1, NUM_RECORDS)
        doctor_id = random.randint(1, NUM_RECORDS)
        visit_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365), hours=random.randint(8, 17))
        diagnosis = random.choice(diagnoses)
        writer.writerow([i, patient_id, doctor_id, visit_date.strftime('%Y-%m-%d %H:%M:%S'), diagnosis])

# 6. PRESCRIPTIONS
with open('Data/PRESCRIPTIONS.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['prescription_id', 'visit_id', 'medicine_name', 'dosage', 'instructions'])
    for i in range(1, NUM_RECORDS + 1):
        visit_id = random.randint(1, NUM_RECORDS)
        medicine = random.choice(medicines)
        dosage = random.choice(["10mg", "20mg", "50mg", "200mg", "500mg"])
        instructions = random.choice(["Take once daily", "Take twice daily after meals", "Take as needed for pain"])
        writer.writerow([i, visit_id, medicine, dosage, instructions])

# 7. VISIT_SERVICES
with open('Data/VISIT_SERVICES.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['vs_id', 'visit_id', 'service_id'])
    for i in range(1, NUM_RECORDS + 1):
        visit_id = random.randint(1, NUM_RECORDS)
        service_id = random.randint(1, NUM_RECORDS)
        writer.writerow([i, visit_id, service_id])

# 8. BILLS
# Calculate total amounts based on VISIT_SERVICES for realism
visit_totals = {}
with open('Data/VISIT_SERVICES.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        v_id = int(row['visit_id'])
        # Assign a random reasonable price for simplicity instead of re-reading services file
        price = round(random.uniform(25.0, 300.0), 2)
        visit_totals[v_id] = visit_totals.get(v_id, 0) + price

with open('Data/BILLS.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['bill_id', 'visit_id', 'total_amount', 'status'])
    for i in range(1, NUM_RECORDS + 1):
        total = round(visit_totals.get(i, random.uniform(50.0, 150.0)), 2) # Fallback if visit had no services
        status = random.choice(["Paid", "Unpaid", "Paid"]) # 2/3 chance of Paid
        writer.writerow([i, i, total, status])

print(f"Successfully generated {NUM_RECORDS} rows of dummy data for all 8 tables in the Data/ directory.")
