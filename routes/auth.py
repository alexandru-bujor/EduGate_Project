from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.db import get_db_connection
from routes.user_management import verify_password
from bson.objectid import ObjectId

auth_bp = Blueprint('auth', __name__)

# ------------------ LOGIN ROUTE ------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db_connection()
        pbl_db_collection = db['pbl_db']

        # Fetch the user data from the 'users' table document
        users_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'users'})
        if users_doc and 'data' in users_doc:
            # Iterate through the users in the 'data' array
            for user in users_doc['data']:
                print(f"Checking user: {user['username']}")

                # Check if the username and password match
                if user.get('username') == username:
                    password_match = verify_password(user['password_hash'], password)
                    if password_match:
                        session['user_id'] = user.get('user_id')
                        session['role'] = user.get('role')

                        print(f"Login successful for user: {user['username']}, Role: {user['role']}")

                        # Redirect based on the user's role
                        if user['role'] == 'Admin':
                            return redirect(url_for('dashboard.admin_dashboard'))
                        elif user['role'] == 'Student':
                            return redirect(url_for('dashboard.student_dashboard'))
                        elif user['role'] == 'Teacher':
                            return redirect(url_for('dashboard.teacher_dashboard'))
                        elif user['role'] == 'Parent':
                            return redirect(url_for('dashboard.parent_dashboard'))
                        else:
                            flash('Invalid role')
                            return render_template('login.html', action="Invalid role!")
                    else:
                        flash('Invalid password')
                        return render_template('login.html', action="Invalid password!")
                else:
                    flash('Username not found')
                    return render_template('login.html', action="Invalid username!")

        flash('Invalid username or password')
        print("Login failed: Invalid username or password")
        return redirect(url_for('auth.login'))

    return render_template('login.html')


# ------------------ LOGOUT ROUTE ------------------
@auth_bp.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('index.index'))
