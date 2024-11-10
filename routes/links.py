import mysql
from flask import Blueprint, request, redirect, url_for, flash, session
from utils.db import get_db_connection

links = Blueprint('links', __name__)

# ------------------ LINK TEACHER TO CLASS ROUTE ------------------
@links.route('/link_teacher_to_class', methods=['POST'])
def link_teacher_to_class():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))  # Only allow admins to access this page

    class_id = request.form['class_id']
    teacher_user_id = request.form['teacher_id']

    # Establish the database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve the teacher_id from the teachers table using the user_id
    cursor.execute("SELECT teacher_id FROM teachers WHERE user_id = %s", (teacher_user_id,))
    teacher = cursor.fetchone()

    if not teacher:
        flash("Teacher not found.")
        return redirect(url_for('dashboard.admin_dashboard'))

    teacher_id = teacher[0]

    # Update the class to link the teacher
    try:
        cursor.execute("UPDATE classes SET teacher_id = %s WHERE class_id = %s", (teacher_id, class_id))
        conn.commit()
    except mysql.connector.Error as err:
        flash(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('dashboard.admin_dashboard', action='link_teacher_to_class_success'))


# ------------------ LINK STUDENT TO CLASS ROUTE ------------------
@links.route('/link_student_class', methods=['POST'])
def link_student_class():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))

    student_id = request.form['student_id']
    class_id = request.form['class_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE students SET class_id = %s WHERE student_id = %s", (class_id, student_id))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('dashboard.admin_dashboard', action='link_student_to_class_success'))

# ------------------ LINK STUDENT TO PARENT ROUTE ------------------
@links.route('/link_student_parent', methods=['POST'])
def link_student_parent():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))

    student_id = request.form['student_id']
    parent_id = request.form['parent_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE students SET parent_id = %s WHERE student_id = %s", (parent_id, student_id))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('dashboard.admin_dashboard', action='link_student_to_parent_success'))
