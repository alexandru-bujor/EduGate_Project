from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')


# ------------------ DATABASE CONNECTION FUNCTION ------------------
def get_db_connection():
    client = MongoClient(
        "mongodb+srv://sandumagla:QHpB0YxzKyhPLmuw@test.zpzjq.mongodb.net/School_Access?retryWrites=true&w=majority")
    return client['School_Acces']


# ------------------ MAIN INDEX ROUTE ------------------
@app.route('/')
def index():
    return render_template('index.html')


# ------------------ LOGIN ROUTE ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phonenumber']
        password = request.form['password']

        db = get_db_connection()
        pbl_db_collection = db['pbl_db']

        # Fetch the user data from the 'users' table document
        users_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'users'})
        if users_doc and 'data' in users_doc:
            # Iterate through the users in the 'data' array
            for user in users_doc['data']:
                print(f"Checking user: {user['username']} with phone: {user['phone_number']}")

                if user.get('phone_number') == phone and user.get('password_hash') == password:
                    session['user_id'] = user.get('user_id')
                    session['role'] = user.get('role')

                    print(f"Login successful for user: {user['username']}, Role: {user['role']}")

                    # Redirect based on the user's role
                    if user['role'] == 'Admin':
                        return redirect(url_for('admin_dashboard'))
                    elif user['role'] == 'Student':
                        return redirect(url_for('student_dashboard'))
                    elif user['role'] == 'Teacher':
                        return redirect(url_for('teacher_dashboard'))
                    elif user['role'] == 'Parent':
                        return redirect(url_for('parents_dashboard'))
                    else:
                        flash('Invalid role')
                        return redirect(url_for('login'))

        flash('Invalid credentials')
        print("Login failed: Invalid credentials")
        return redirect(url_for('login'))

    return render_template('login.html')



# ------------------ STUDENT DASHBOARD ROUTE ------------------
@app.route('/student_dashboard')
def student_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    db = get_db_connection()
    pbl_db_collection = db['pbl_db']
    users_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'users'})
    user = next((u for u in users_doc['data'] if u.get('user_id') == user_id), None)

    return render_template('student_dashboard.html', user=user)


# ------------------ ADD USER ROUTE ------------------
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))

    db = get_db_connection()
    pbl_db_collection = db['pbl_db']

    if request.method == 'POST':
        # Retrieve form data
        user_data = {
            'user_id': str(ObjectId()),  # Generate a unique user ID
            'username': request.form['username'],
            'password_hash': request.form['password'],  # Store plaintext password for now
            'email': request.form['email'],
            'phone_number': request.form['phone_number'],
            'role': request.form['role'],
            'full_name': request.form['full_name'],
            'profile_picture': request.form.get('profile_picture', ''),
            'created_at': request.form.get('created_at', '')
        }

        # Insert the new user into the 'users' data array
        users_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'users'})
        if users_doc:
            pbl_db_collection.update_one(
                {'type': 'table', 'name': 'users'},
                {'$push': {'data': user_data}}
            )
            flash('User added successfully!')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Users table not found.')
            return redirect(url_for('admin_dashboard'))

    return render_template('add_user.html')


# ------------------ TEACHER DASHBOARD ROUTE ------------------
@app.route('/teacher_dashboard')
def teacher_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    db = get_db_connection()
    pbl_db_collection = db['pbl_db']
    users_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'users'})
    teacher = next((u for u in users_doc['data'] if u.get('user_id') == user_id), None)

    return render_template('teacher_dashboard.html', teacher=teacher)


# ------------------ PARENT DASHBOARD ROUTE ------------------
@app.route('/parent_dashboard')
def parents_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    db = get_db_connection()
    pbl_db_collection = db['pbl_db']
    users_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'users'})
    parent = next((u for u in users_doc['data'] if u.get('user_id') == user_id), None)

    return render_template('parent_dashboard.html', parent=parent)


# ------------------ ADMIN DASHBOARD ROUTE ------------------
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))

    db = get_db_connection()
    pbl_db_collection = db['pbl_db']
    users_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'users'})
    admin = next((u for u in users_doc['data'] if u.get('user_id') == session['user_id']), None)

    return render_template('admin_dashboard.html', admin=admin)


# ------------------ LOGOUT ROUTE ------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)

