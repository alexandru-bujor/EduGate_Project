from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.db import get_db_connection
from routes.user_management import verify_password
auth_bp = Blueprint('auth', __name__)

# ------------------ LOGIN ROUTE ------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        password_match = verify_password(user['password_hash'], password)

        if user and password_match:  # Consider hashing and checking the password
            session['user_id'] = user['user_id']  # Store user id in session
            session['role'] = user['role']  # Store user role in session

            # Redirect to different dashboards based on role
            if user['role'] == 'Student':
                return redirect(url_for('dashboard.student_dashboard'))
            elif user['role'] == 'Teacher':
                return redirect(url_for('dashboard.teacher_dashboard'))
            elif user['role'] == 'Parent':
                return redirect(url_for('dashboard.parent_dashboard'))
            elif user['role'] == 'Admin':
                return redirect(url_for('dashboard.admin_dashboard'))
            else:
                flash('Invalid role')
                return redirect(url_for('auth.login'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


# ------------------ LOGOUT ROUTE ------------------
@auth_bp.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('index.index'))
