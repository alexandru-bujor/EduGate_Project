from flask import Blueprint, request, redirect, url_for, flash, session
from utils.db import get_db_connection
from argon2 import PasswordHasher

ph = PasswordHasher()
user_management_bp = Blueprint('user_management', __name__)

def hash_password(password):
    return ph.hash(password)

def verify_password(stored_hash, provided_password):
    try:
        ph.verify(stored_hash, provided_password)
        return True
    except:
        return False

@user_management_bp.route('/add_user', methods=['POST'])
def add_user():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('auth.login'))

    # Get form data
    full_name = request.form['full_name']
    username = request.form['username']
    password = request.form['password']
    password_hash = hash_password(password)
    email = request.form['email']
    phone_number = request.form['phone_number']
    role = request.form['role']
    profile_picture = request.form['profile_picture']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert into users table
    cursor.execute("""
        INSERT INTO users (username, password_hash, full_name, email, phone_number, role, profile_picture) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (username, password_hash, full_name, email, phone_number, role, profile_picture))
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

    return redirect(url_for('dashboard.admin_dashboard', action='add_user_success'))


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

    return redirect(url_for('dashboard.admin_dashboard', action='delete_user_success'))