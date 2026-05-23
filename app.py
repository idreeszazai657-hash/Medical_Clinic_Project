import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'medical_clinic_secret_key_2026'

# ─── Database ────────────────────────────────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '8920',
    'database': 'medical_clinic',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': True
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

# ─── Auth Decorator ──────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'Admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# ─── Create default admin on startup ─────────────────────────────────────
def ensure_default_admin():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM USERS WHERE username = %s", ('admin',))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO USERS (username, password_hash, role, first_name, last_name) VALUES (%s, %s, %s, %s, %s)",
                    ('admin', 'admin123', 'Admin', 'System', 'Admin')
                )
    finally:
        conn.close()

# ─── Routes: Auth ────────────────────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM USERS WHERE username = %s", (username,))
                user = cur.fetchone()
        finally:
            conn.close()
        if user and user['password_hash'] == password:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['first_name'] = user['first_name']
            session['last_name'] = user['last_name']
            flash(f'Welcome back, {user["first_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ─── Routes: Dashboard ──────────────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c FROM PATIENTS")
            total_patients = cur.fetchone()['c']
            cur.execute("SELECT COUNT(*) AS c FROM DOCTORS")
            total_doctors = cur.fetchone()['c']
            cur.execute("SELECT COUNT(*) AS c FROM VISITS")
            total_visits = cur.fetchone()['c']
            cur.execute("SELECT COALESCE(SUM(total_amount),0) AS c FROM BILLS WHERE status='Paid'")
            total_revenue = cur.fetchone()['c']
            cur.execute("SELECT COUNT(*) AS c FROM BILLS WHERE status='Unpaid'")
            unpaid_bills = cur.fetchone()['c']
            cur.execute("""
                SELECT v.visit_id, p.first_name AS pf, p.last_name AS pl,
                       d.first_name AS df, d.last_name AS dl,
                       v.visit_date, v.diagnosis
                FROM VISITS v
                JOIN PATIENTS p ON v.patient_id=p.patient_id
                JOIN DOCTORS d ON v.doctor_id=d.doctor_id
                ORDER BY v.visit_date DESC LIMIT 10
            """)
            recent_visits = cur.fetchall()
            cur.execute("""
                SELECT MONTH(visit_date) AS m, COUNT(*) AS c
                FROM VISITS GROUP BY MONTH(visit_date) ORDER BY m
            """)
            visits_by_month = cur.fetchall()
            cur.execute("""
                SELECT d.specialty, COUNT(*) AS c
                FROM DOCTORS d GROUP BY d.specialty ORDER BY c DESC LIMIT 8
            """)
            specialties = cur.fetchall()
    finally:
        conn.close()
    return render_template('dashboard.html',
        total_patients=total_patients, total_doctors=total_doctors,
        total_visits=total_visits, total_revenue=total_revenue,
        unpaid_bills=unpaid_bills, recent_visits=recent_visits,
        visits_by_month=visits_by_month, specialties=specialties)

# ─── Routes: Patients ───────────────────────────────────────────────────
@app.route('/patients')
@login_required
def patients():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM PATIENTS ORDER BY patient_id DESC")
            rows = cur.fetchall()
    finally:
        conn.close()
    return render_template('patients.html', patients=rows)

@app.route('/patients/add', methods=['POST'])
@login_required
def patient_add():
    fn = request.form['first_name'].strip()
    ln = request.form['last_name'].strip()
    dob = request.form['dob']
    gender = request.form['gender']
    contact = request.form['contact'].strip()
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO PATIENTS (first_name,last_name,dob,gender,contact) VALUES (%s,%s,%s,%s,%s)",
                        (fn, ln, dob, gender, contact))
    finally:
        conn.close()
    flash('Patient registered successfully!', 'success')
    return redirect(url_for('patients'))

@app.route('/patients/edit/<int:pid>', methods=['POST'])
@login_required
def patient_edit(pid):
    fn = request.form['first_name'].strip()
    ln = request.form['last_name'].strip()
    dob = request.form['dob']
    gender = request.form['gender']
    contact = request.form['contact'].strip()
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE PATIENTS SET first_name=%s,last_name=%s,dob=%s,gender=%s,contact=%s WHERE patient_id=%s",
                        (fn, ln, dob, gender, contact, pid))
    finally:
        conn.close()
    flash('Patient updated.', 'success')
    return redirect(url_for('patients'))

@app.route('/patients/delete/<int:pid>', methods=['POST'])
@login_required
def patient_delete(pid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM PATIENTS WHERE patient_id=%s", (pid,))
    finally:
        conn.close()
    flash('Patient deleted.', 'success')
    return redirect(url_for('patients'))

# ─── Routes: Doctors ─────────────────────────────────────────────────────
@app.route('/doctors')
@login_required
def doctors():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM DOCTORS ORDER BY doctor_id DESC")
            rows = cur.fetchall()
            cur.execute("SELECT DISTINCT specialty FROM DOCTORS ORDER BY specialty")
            specs = cur.fetchall()
    finally:
        conn.close()
    return render_template('doctors.html', doctors=rows, specialties=specs)

@app.route('/doctors/add', methods=['POST'])
@login_required
def doctor_add():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO DOCTORS (first_name,last_name,specialty,contact,room_number) VALUES (%s,%s,%s,%s,%s)",
                (request.form['first_name'].strip(), request.form['last_name'].strip(),
                 request.form['specialty'].strip(), request.form['contact'].strip(),
                 request.form['room_number'].strip()))
    finally:
        conn.close()
    flash('Doctor added.', 'success')
    return redirect(url_for('doctors'))

@app.route('/doctors/edit/<int:did>', methods=['POST'])
@login_required
def doctor_edit(did):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE DOCTORS SET first_name=%s,last_name=%s,specialty=%s,contact=%s,room_number=%s WHERE doctor_id=%s",
                (request.form['first_name'].strip(), request.form['last_name'].strip(),
                 request.form['specialty'].strip(), request.form['contact'].strip(),
                 request.form['room_number'].strip(), did))
    finally:
        conn.close()
    flash('Doctor updated.', 'success')
    return redirect(url_for('doctors'))

@app.route('/doctors/delete/<int:did>', methods=['POST'])
@login_required
def doctor_delete(did):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM DOCTORS WHERE doctor_id=%s", (did,))
    finally:
        conn.close()
    flash('Doctor deleted.', 'success')
    return redirect(url_for('doctors'))

# ─── Routes: Visits ──────────────────────────────────────────────────────
@app.route('/visits')
@login_required
def visits():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT v.*, p.first_name AS pf, p.last_name AS pl,
                       d.first_name AS df, d.last_name AS dl, d.specialty
                FROM VISITS v
                JOIN PATIENTS p ON v.patient_id=p.patient_id
                JOIN DOCTORS d ON v.doctor_id=d.doctor_id
                ORDER BY v.visit_date DESC
            """)
            rows = cur.fetchall()
            cur.execute("SELECT patient_id, first_name, last_name FROM PATIENTS ORDER BY first_name")
            pat_list = cur.fetchall()
            cur.execute("SELECT doctor_id, first_name, last_name, specialty FROM DOCTORS ORDER BY first_name")
            doc_list = cur.fetchall()
    finally:
        conn.close()
    return render_template('visits.html', visits=rows, patients=pat_list, doctors=doc_list)

@app.route('/visits/add', methods=['POST'])
@login_required
def visit_add():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO VISITS (patient_id,doctor_id,visit_date,diagnosis) VALUES (%s,%s,%s,%s)",
                (request.form['patient_id'], request.form['doctor_id'],
                 request.form['visit_date'], request.form.get('diagnosis','')))
    finally:
        conn.close()
    flash('Visit created.', 'success')
    return redirect(url_for('visits'))

@app.route('/visits/<int:vid>')
@login_required
def visit_detail(vid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT v.*, p.first_name AS pf, p.last_name AS pl, p.contact AS pc, p.gender,
                       d.first_name AS df, d.last_name AS dl, d.specialty, d.room_number
                FROM VISITS v
                JOIN PATIENTS p ON v.patient_id=p.patient_id
                JOIN DOCTORS d ON v.doctor_id=d.doctor_id
                WHERE v.visit_id=%s
            """, (vid,))
            visit = cur.fetchone()
            if not visit:
                flash('Visit not found.', 'danger')
                return redirect(url_for('visits'))
            cur.execute("SELECT * FROM PRESCRIPTIONS WHERE visit_id=%s ORDER BY prescription_id", (vid,))
            prescriptions = cur.fetchall()
            cur.execute("""
                SELECT vs.vs_id, ms.service_id, ms.service_name, ms.price
                FROM VISIT_SERVICES vs
                JOIN MEDICAL_SERVICES ms ON vs.service_id=ms.service_id
                WHERE vs.visit_id=%s
            """, (vid,))
            v_services = cur.fetchall()
            cur.execute("SELECT * FROM BILLS WHERE visit_id=%s", (vid,))
            bill = cur.fetchone()
            cur.execute("SELECT service_id, service_name, price FROM MEDICAL_SERVICES ORDER BY service_name")
            all_services = cur.fetchall()
    finally:
        conn.close()
    return render_template('visit_detail.html', visit=visit, prescriptions=prescriptions,
                           visit_services=v_services, bill=bill, all_services=all_services)

@app.route('/visits/delete/<int:vid>', methods=['POST'])
@login_required
def visit_delete(vid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM VISITS WHERE visit_id=%s", (vid,))
    finally:
        conn.close()
    flash('Visit deleted.', 'success')
    return redirect(url_for('visits'))

# ─── Routes: Prescriptions ──────────────────────────────────────────────
@app.route('/prescriptions')
@login_required
def prescriptions():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT pr.*, v.visit_date, v.diagnosis,
                       p.first_name AS pf, p.last_name AS pl
                FROM PRESCRIPTIONS pr
                JOIN VISITS v ON pr.visit_id=v.visit_id
                JOIN PATIENTS p ON v.patient_id=p.patient_id
                ORDER BY pr.prescription_id DESC
            """)
            rows = cur.fetchall()
            cur.execute("""
                SELECT v.visit_id, v.visit_date, p.first_name, p.last_name
                FROM VISITS v JOIN PATIENTS p ON v.patient_id=p.patient_id
                ORDER BY v.visit_date DESC
            """)
            visit_list = cur.fetchall()
    finally:
        conn.close()
    return render_template('prescriptions.html', prescriptions=rows, visits=visit_list)

@app.route('/prescriptions/add', methods=['POST'])
@login_required
def prescription_add():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO PRESCRIPTIONS (visit_id,medicine_name,dosage,instructions) VALUES (%s,%s,%s,%s)",
                (request.form['visit_id'], request.form['medicine_name'].strip(),
                 request.form['dosage'].strip(), request.form.get('instructions','')))
    finally:
        conn.close()
    flash('Prescription added.', 'success')
    ref = request.form.get('redirect_to','')
    if ref:
        return redirect(ref)
    return redirect(url_for('prescriptions'))

@app.route('/prescriptions/delete/<int:pid>', methods=['POST'])
@login_required
def prescription_delete(pid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM PRESCRIPTIONS WHERE prescription_id=%s", (pid,))
    finally:
        conn.close()
    flash('Prescription deleted.', 'success')
    ref = request.form.get('redirect_to','')
    if ref:
        return redirect(ref)
    return redirect(url_for('prescriptions'))

# ─── Routes: Services ───────────────────────────────────────────────────
@app.route('/services')
@login_required
def services():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM MEDICAL_SERVICES ORDER BY service_id")
            rows = cur.fetchall()
    finally:
        conn.close()
    return render_template('services.html', services=rows)

@app.route('/services/add', methods=['POST'])
@login_required
def service_add():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO MEDICAL_SERVICES (service_name,price) VALUES (%s,%s)",
                (request.form['service_name'].strip(), request.form['price']))
    finally:
        conn.close()
    flash('Service added.', 'success')
    return redirect(url_for('services'))

@app.route('/services/edit/<int:sid>', methods=['POST'])
@login_required
def service_edit(sid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE MEDICAL_SERVICES SET service_name=%s,price=%s WHERE service_id=%s",
                (request.form['service_name'].strip(), request.form['price'], sid))
    finally:
        conn.close()
    flash('Service updated.', 'success')
    return redirect(url_for('services'))

@app.route('/services/delete/<int:sid>', methods=['POST'])
@login_required
def service_delete(sid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM MEDICAL_SERVICES WHERE service_id=%s", (sid,))
    finally:
        conn.close()
    flash('Service deleted.', 'success')
    return redirect(url_for('services'))

# ─── Routes: Visit Services ─────────────────────────────────────────────
def update_bill_total(cur, visit_id):
    cur.execute("SELECT bill_id FROM BILLS WHERE visit_id = %s", (visit_id,))
    if cur.fetchone():
        cur.execute("""
            SELECT COALESCE(SUM(ms.price), 0) AS total 
            FROM VISIT_SERVICES vs
            JOIN MEDICAL_SERVICES ms ON vs.service_id = ms.service_id
            WHERE vs.visit_id = %s
        """, (visit_id,))
        new_total = cur.fetchone()['total']
        cur.execute("UPDATE BILLS SET total_amount = %s WHERE visit_id = %s", (new_total, visit_id))

@app.route('/visit-services/add', methods=['POST'])
@login_required
def visit_service_add():
    visit_id = request.form['visit_id']
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO VISIT_SERVICES (visit_id,service_id) VALUES (%s,%s)",
                (visit_id, request.form['service_id']))
            update_bill_total(cur, visit_id)
    finally:
        conn.close()
    flash('Service assigned to visit. Bill automatically updated if exists.', 'success')
    return redirect(url_for('visit_detail', vid=visit_id))

@app.route('/visit-services/delete/<int:vsid>', methods=['POST'])
@login_required
def visit_service_delete(vsid):
    vid = request.form.get('visit_id')
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM VISIT_SERVICES WHERE vs_id=%s", (vsid,))
            update_bill_total(cur, vid)
    finally:
        conn.close()
    flash('Service removed from visit. Bill automatically updated if exists.', 'success')
    return redirect(url_for('visit_detail', vid=vid))

# ─── Routes: Bills ───────────────────────────────────────────────────────
@app.route('/bills')
@login_required
def bills():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT b.*, v.visit_date, v.diagnosis,
                       p.first_name AS pf, p.last_name AS pl
                FROM BILLS b
                JOIN VISITS v ON b.visit_id=v.visit_id
                JOIN PATIENTS p ON v.patient_id=p.patient_id
                ORDER BY b.bill_id DESC
            """)
            rows = cur.fetchall()
            cur.execute("SELECT COALESCE(SUM(total_amount),0) AS t FROM BILLS WHERE status='Paid'")
            total_paid = cur.fetchone()['t']
            cur.execute("SELECT COALESCE(SUM(total_amount),0) AS t FROM BILLS WHERE status='Unpaid'")
            total_unpaid = cur.fetchone()['t']
    finally:
        conn.close()
    return render_template('bills.html', bills=rows, total_paid=total_paid, total_unpaid=total_unpaid)

@app.route('/bills/add', methods=['POST'])
@login_required
def bill_add():
    visit_id = request.form['visit_id']
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Auto-calculate the total amount from assigned medical services
            cur.execute("""
                SELECT COALESCE(SUM(ms.price), 0) AS total 
                FROM VISIT_SERVICES vs
                JOIN MEDICAL_SERVICES ms ON vs.service_id = ms.service_id
                WHERE vs.visit_id = %s
            """, (visit_id,))
            total_amount = cur.fetchone()['total']
            
            cur.execute("INSERT INTO BILLS (visit_id,total_amount,status) VALUES (%s,%s,%s)",
                (visit_id, total_amount, request.form.get('status','Unpaid')))
    finally:
        conn.close()
    flash('Bill created and automatically calculated from assigned services.', 'success')
    ref = request.form.get('redirect_to','')
    if ref:
        return redirect(ref)
    return redirect(url_for('bills'))

@app.route('/bills/pay/<int:bid>', methods=['POST'])
@login_required
def bill_pay(bid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE BILLS SET status='Paid' WHERE bill_id=%s", (bid,))
    finally:
        conn.close()
    flash('Bill marked as paid.', 'success')
    ref = request.form.get('redirect_to','')
    if ref:
        return redirect(ref)
    return redirect(url_for('bills'))

@app.route('/bills/delete/<int:bid>', methods=['POST'])
@login_required
def bill_delete(bid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM BILLS WHERE bill_id=%s", (bid,))
    finally:
        conn.close()
    flash('Bill deleted.', 'success')
    return redirect(url_for('bills'))

# ─── Routes: Users (Admin only) ─────────────────────────────────────────
@app.route('/users')
@admin_required
def users():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, username, role, first_name, last_name FROM USERS ORDER BY user_id")
            rows = cur.fetchall()
    finally:
        conn.close()
    return render_template('users.html', users=rows)

@app.route('/users/add', methods=['POST'])
@admin_required
def user_add():
    username = request.form['username'].strip()
    password = request.form['password']
    role = request.form['role']
    fn = request.form['first_name'].strip()
    ln = request.form['last_name'].strip()
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM USERS WHERE username=%s", (username,))
            if cur.fetchone():
                flash('Username already exists.', 'danger')
                return redirect(url_for('users'))
            cur.execute("INSERT INTO USERS (username,password_hash,role,first_name,last_name) VALUES (%s,%s,%s,%s,%s)",
                (username, password, role, fn, ln))
    finally:
        conn.close()
    flash('User created.', 'success')
    return redirect(url_for('users'))

@app.route('/users/reset-password/<int:uid>', methods=['POST'])
@admin_required
def user_reset_password(uid):
    new_pw = request.form['new_password']
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE USERS SET password_hash=%s WHERE user_id=%s", (new_pw, uid))
    finally:
        conn.close()
    flash('Password reset successfully.', 'success')
    return redirect(url_for('users'))

@app.route('/users/delete/<int:uid>', methods=['POST'])
@admin_required
def user_delete(uid):
    if uid == session.get('user_id'):
        flash('Cannot delete your own account.', 'danger')
        return redirect(url_for('users'))
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM USERS WHERE user_id=%s", (uid,))
    finally:
        conn.close()
    flash('User deleted.', 'success')
    return redirect(url_for('users'))

# ─── Run ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    ensure_default_admin()
    app.run(debug=True, port=5000)
