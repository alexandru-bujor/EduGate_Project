from flask import Blueprint, request, redirect, url_for, render_template, session
from utils.db import get_db_connection

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/record_attendance', methods=['POST'])
def record_attendance():
    student_id = request.form['student_id']
    entry_time = request.form['entry_time']
    exit_time = request.form['exit_time']
    face_confirmation = request.form['face_confirmation']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO attendance (student_id, entry_time, exit_time, face_confirmation) 
        VALUES (%s, %s, %s, %s)
    """, (student_id, entry_time, exit_time, face_confirmation))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('dashboard.admin_dashboard'))

@attendance_bp.route('/view_attendance/<int:student_id>', methods=['GET'])
def view_attendance(student_id):
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT student_id, uid, entry_time, exit_time, face_confirmation 
        FROM attendance 
        WHERE student_id = %s
    """, (student_id,))
    records = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('view_attendance.html', records=records)
