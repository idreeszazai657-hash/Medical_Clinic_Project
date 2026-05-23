import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '8920',
    'database': 'medical_clinic',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': True
}

def fix_passwords_to_plaintext():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            # Set all passwords to 'password123' except admin
            cur.execute("UPDATE USERS SET password_hash = 'password123' WHERE username != 'admin'")
            
            # Set admin password to 'admin123'
            cur.execute("UPDATE USERS SET password_hash = 'admin123' WHERE username = 'admin'")
            
            print("Successfully updated all user passwords to plaintext.")
    finally:
        conn.close()

if __name__ == '__main__':
    fix_passwords_to_plaintext()
