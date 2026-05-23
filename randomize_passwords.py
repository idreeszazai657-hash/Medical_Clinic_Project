import pymysql
import random
import string
import csv

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '8920',
    'database': 'medical_clinic',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': True
}

def generate_random_password(length=8):
    """Generate a random alphanumeric password."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def randomize_passwords():
    conn = pymysql.connect(**DB_CONFIG)
    user_passwords = []
    try:
        with conn.cursor() as cur:
            # Get all users except admin
            cur.execute("SELECT user_id, username, first_name, last_name FROM USERS WHERE username != 'admin'")
            users = cur.fetchall()
            
            for user in users:
                new_password = generate_random_password()
                
                # Update the database with the plaintext random password
                cur.execute(
                    "UPDATE USERS SET password_hash = %s WHERE user_id = %s",
                    (new_password, user['user_id'])
                )
                
                # Save mapping for the CSV report
                user_passwords.append({
                    'Username': user['username'],
                    'Name': f"{user['first_name']} {user['last_name']}",
                    'Password': new_password
                })
                
            print(f"Successfully generated random passwords for {len(users)} users.")
            
    finally:
        conn.close()
        
    # Write the passwords to a CSV file so the user has a record of them
    if user_passwords:
        csv_filename = 'user_passwords.csv'
        with open(csv_filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['Username', 'Name', 'Password'])
            writer.writeheader()
            writer.writerows(user_passwords)
        print(f"A record of all the new passwords has been saved to: {csv_filename}")

if __name__ == '__main__':
    randomize_passwords()
