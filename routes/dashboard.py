import datetime

from flask import Blueprint, render_template, session, redirect, url_for
from utils.db import get_db_connection

dashboard_bp = Blueprint('dashboard', __name__)


# ------------------ ADMIN DASHBOARD ROUTE ------------------
@dashboard_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))  # Only allow admins to access this page

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch admin details
    cursor.execute("SELECT full_name, profile_picture FROM users WHERE user_id = %s", (user_id,))
    admin = cursor.fetchone()

    # Fetch teachers with their details
    cursor.execute("""
        SELECT u.user_id, u.full_name, u.email, u.phone_number, u.profile_picture
        FROM users u
        JOIN teachers t ON u.user_id = t.user_id
    """)
    teachers = cursor.fetchall()

    # Fetch parents with their details
    cursor.execute("""
        SELECT u.user_id, u.full_name, u.email, u.phone_number, u.profile_picture, p.parent_id
        FROM users u
        JOIN parents p ON u.user_id = p.user_id
    """)
    parents = cursor.fetchall()

    # Fetch students with details, including linked parent and class information
    cursor.execute("""
        SELECT s.student_id, s.user_id, u.full_name AS student_name, s.class_id, s.parent_id, u.email, u.phone_number, u.profile_picture,
               c.class_name, c.description AS class_description, pu.full_name AS parent_name
        FROM students s
        JOIN users u ON s.user_id = u.user_id
        LEFT JOIN classes c ON s.class_id = c.class_id
        LEFT JOIN parents p ON s.parent_id = p.parent_id
        LEFT JOIN users pu ON p.user_id = pu.user_id
    """)
    students = cursor.fetchall()

    # Fetch all users for user management
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    # Fetch all classes with linked teacher information
    cursor.execute("""
        SELECT c.class_id, c.class_name, c.description, t.teacher_id, u.full_name AS teacher_name, u.profile_picture AS teacher_picture
        FROM classes c
        LEFT JOIN teachers t ON c.teacher_id = t.teacher_id
        LEFT JOIN users u ON t.user_id = u.user_id
    """)
    classes = cursor.fetchall()

    # Close the connection
    conn.close()

    # Render the template with all the data
    return render_template(
        'admin_dashboard.html',
        admin=admin,
        users=users,
        classes=classes,
        students=students,
        teachers=teachers,
        parents=parents
    )


# ------------------ STUDENT DASHBOARD ROUTE ------------------
@dashboard_bp.route('/student_dashboard')
def student_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')  # Redirect if user is not logged in

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch student details
    cursor.execute("""
        SELECT u.full_name AS student_name, u.profile_picture
        FROM users u 
        JOIN students s ON u.user_id = s.user_id 
        WHERE u.user_id = %s
    """, (user_id,))
    user = cursor.fetchone()

    # Fetch the parent details of the student
    cursor.execute("""
        SELECT pu.full_name AS parent_name
        FROM students s
        JOIN parents p ON s.parent_id = p.parent_id
        JOIN users pu ON p.user_id = pu.user_id
        WHERE s.user_id = %s
    """, (user_id,))
    parent = cursor.fetchone()

    # Fetch attendance records for the student
    cursor.execute("""
        SELECT a.uid, a.entry_time, a.exit_time, a.face_confirmation 
        FROM attendance a 
        WHERE a.student_id = (SELECT student_id FROM students WHERE user_id = %s) 
        ORDER BY a.entry_time DESC
    """, (user_id,))
    attendance_records = cursor.fetchall()

    conn.close()

    return render_template('student_dashboard.html', user=user, parent=parent, attendance_records=attendance_records)


# ------------------ TEACHER DASHBOARD ROUTE ------------------
@dashboard_bp.route('/teacher_dashboard')
def teacher_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')  # Redirect if user is not logged in

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch teacher details
    cursor.execute("""
        SELECT u.full_name, u.profile_picture
        FROM users u
        JOIN teachers t ON u.user_id = t.user_id
        WHERE u.user_id = %s
    """, (user_id,))
    teacher = cursor.fetchone()

    if not teacher:
        return "Teacher not found or not linked properly."

    # You can add additional data fetching as needed for the teacher

    conn.close()
    return render_template('teacher_dashboard.html', teacher=teacher)


# ------------------ PARENT DASHBOARD ROUTE ------------------
@dashboard_bp.route('/parent_dashboard')
def parent_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch parent details along with parent_id and profile picture
    cursor.execute("""
        SELECT u.*, p.parent_id 
        FROM users u 
        JOIN parents p ON u.user_id = p.user_id 
        WHERE u.user_id = %s
    """, (user_id,))
    parent = cursor.fetchone()

    if not parent:
        return "Parent not found or not linked properly."

    # Fetch students linked to this parent with their profile pictures
    cursor.execute("""
        SELECT 
            s.student_id,
            u.full_name AS student_full_name,
            u.profile_picture AS student_profile_picture,  -- Fetching student's profile picture
            p.parent_id,
            parent_user.full_name AS parent_full_name,
            parent_user.profile_picture AS parent_profile_picture  -- Fetching parent's profile picture
        FROM 
            students s
        JOIN 
            users u ON s.user_id = u.user_id
        JOIN 
            parents p ON s.parent_id = p.parent_id
        JOIN 
            users parent_user ON p.user_id = parent_user.user_id
        WHERE 
            p.parent_id = %s
        ORDER BY 
            s.student_id;
    """, (parent['parent_id'],))
    students = cursor.fetchall()

    # For each student, fetch their attendance history and calculate stats
    for student in students:
        cursor.execute("""
            SELECT a.entry_time, a.exit_time, a.face_confirmation 
            FROM attendance a
            WHERE a.student_id = %s
            ORDER BY a.entry_time DESC
        """, (student['student_id'],))
        attendance_records = cursor.fetchall()

        student['attendance_records'] = attendance_records

        # Initialize attendance stats
        on_time = late = absent = 0
        total_records = len(attendance_records)

        for record in attendance_records:
            entry_time = record['entry_time']
            if entry_time is None:
                absent += 1
            elif isinstance(entry_time, datetime.datetime):
                if entry_time.time() <= datetime.time(8, 15):
                    on_time += 1
                else:
                    late += 1

        # Avoid division by zero
        if total_records > 0:
            on_time_percentage = (on_time / total_records) * 100
            late_percentage = (late / total_records) * 100
            absent_percentage = (absent / total_records) * 100
        else:
            on_time_percentage = late_percentage = absent_percentage = 0

        student['attendance_stats'] = {
            'on_time': on_time_percentage,
            'late': late_percentage,
            'absent': absent_percentage
        }

    conn.close()
    return render_template('parent_dashboard.html', parent=parent, students=students)
