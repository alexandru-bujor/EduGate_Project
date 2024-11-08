from flask import Blueprint, request, redirect, url_for, flash, session
from utils.db import get_db_connection

user_management_bp = Blueprint('user_management', __name__)

@user_management_bp.route('/add_user', methods=['POST'])
def add_user():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('auth.login'))

    # Get form data
    full_name = request.form['full_name']
    username = request.form['username']
    password_hash = request.form['password']
    email = request.form['email']
    phone_number = request.form['phone_number']
    role = request.form['role']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert into users table
    cursor.execute("""
        INSERT INTO users (username, password_hash, full_name, email, phone_number, role) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (username, password_hash, full_name, email, phone_number, role))
    user_id = cursor.lastrowid  # Get the ID of the newly created user

    # Insert into role-specific table
    if role == 'Parent':
        cursor.execute("INSERT INTO parents (user_id) VALUES (%s)", (user_id,))
    elif role == 'Teacher':
        cursor.execute("INSERT INTO teachers (user_id) VALUES (%s)", (user_id,))
    elif role == 'Student':
        cursor.execute("INSERT INTO students (user_id) VALUES (%s)", (user_id,))

    conn.commit()
    cursor.close()
    conn.close()

    flash('User added successfully!')
    return redirect(url_for('dashboard.admin_dashboard'))


@user_management_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('User deleted successfully!')
    return redirect(url_for('dashboard.admin_dashboard'))
