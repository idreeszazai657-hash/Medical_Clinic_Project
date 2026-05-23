import pymysql
from werkzeug.security import generate_password_hash

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '8920',
    'database': 'medical_clinic',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': True
}

def fix_passwords():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            # We want to keep the admin user password as is, so we filter it out
            cur.execute("SELECT user_id, username FROM USERS WHERE username != 'admin'")
            users = cur.fetchall()
            
            hashed_pw = generate_password_hash('password123')
            
            for user in users:
                cur.execute(
                    "UPDATE USERS SET password_hash = %s WHERE user_id = %s",
                    (hashed_pw, user['user_id'])
                )
            print(f"Successfully updated passwords for {len(users)} users.")
            print("Their new password is: password123")
    finally:
        conn.close()

if __name__ == '__main__':
    fix_passwords()
