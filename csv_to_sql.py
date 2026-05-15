import csv
import os

# Ensure DML directory exists
os.makedirs('DML', exist_ok=True)

# List of tables in the correct insertion order (due to Foreign Keys)
tables = [
    "USERS",
    "PATIENTS",
    "DOCTORS",
    "MEDICAL_SERVICES",
    "VISITS",
    "PRESCRIPTIONS",
    "VISIT_SERVICES",
    "BILLS"
]

sql_file_path = 'DML/insert_data.sql'

def format_value(val):
    # Try integer
    if val.isdigit():
        return val
    # Try float
    try:
        float(val)
        if '.' in val:
            return val
    except ValueError:
        pass
    
    # Otherwise, it's a string, escape single quotes and return surrounded by single quotes
    escaped_val = val.replace("'", "''")
    return f"'{escaped_val}'"

with open(sql_file_path, 'w', encoding='utf-8') as sql_file:
    sql_file.write("USE medical_clinic;\n\n")
    
    for table in tables:
        csv_file_path = f"Data/{table}.csv"
        if not os.path.exists(csv_file_path):
            print(f"Skipping {table}, CSV not found.")
            continue
            
        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            headers = next(reader)
            
            sql_file.write(f"-- Inserting data into {table}\n")
            
            # Prepare the INSERT INTO statement base
            columns_str = ", ".join(headers)
            
            for row in reader:
                values_str = ", ".join([format_value(val) for val in row])
                sql_file.write(f"INSERT INTO {table} ({columns_str}) VALUES ({values_str});\n")
            
            sql_file.write("\n")

print(f"Successfully generated {sql_file_path}!")
