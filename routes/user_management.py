from flask import Blueprint, request, redirect, url_for, flash, session
from utils.db import get_db_connection
from argon2 import PasswordHasher

ph = PasswordHasher()
user_management_bp = Blueprint('user_management', __name__)

# Password hashing functions
def hash_password(password):
    return ph.hash(password)

def verify_password(stored_hash, provided_password):
    try:
        ph.verify(stored_hash, provided_password)
        return True
    except:
        return False

# ------------------ ADD USER ROUTE ------------------
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

    # Get MongoDB connection
    db = get_db_connection()
    pbl_db_collection = db['pbl_db']

    # Generate a new user ID
    users_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'users'})
    user_id = str(max([int(u.get('user_id', 0)) for u in users_doc['data']], default=0) + 1)

    # Create the new user record
    new_user = {
        'user_id': user_id,
        'username': username,
        'password_hash': password_hash,
        'full_name': full_name,
        'email': email,
        'phone_number': phone_number,
        'role': role,
        'profile_picture': profile_picture
    }

    # Insert the new user into the users table
    pbl_db_collection.update_one(
        {'type': 'table', 'name': 'users'},
        {'$push': {'data': new_user}}
    )

    # Insert into role-specific table
    if role == 'Parent':
        pbl_db_collection.update_one(
            {'type': 'table', 'name': 'parents'},
            {'$push': {'data': {'user_id': user_id, 'parent_id': user_id}}}
        )
    elif role == 'Teacher':
        pbl_db_collection.update_one(
            {'type': 'table', 'name': 'teachers'},
            {'$push': {'data': {'user_id': user_id, 'teacher_id': user_id}}}
        )
    elif role == 'Student':
        pbl_db_collection.update_one(
            {'type': 'table', 'name': 'students'},
            {'$push': {'data': {'user_id': user_id, 'student_id': user_id}}}
        )

    flash("User added successfully.")
    return redirect(url_for('dashboard.admin_dashboard', action='add_user_success'))


# ------------------ DELETE USER ROUTE ------------------
@user_management_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('auth.login'))

    # Convert user_id to string for MongoDB query
    user_id_str = str(user_id)

    # Get MongoDB connection
    db = get_db_connection()
    pbl_db_collection = db['pbl_db']

    # Delete the user from the users table
    result = pbl_db_collection.update_one(
        {'type': 'table', 'name': 'users'},
        {'$pull': {'data': {'user_id': user_id_str}}}
    )

    # Delete the user from role-specific tables
    pbl_db_collection.update_one(
        {'type': 'table', 'name': 'parents'},
        {'$pull': {'data': {'user_id': user_id_str}}}
    )
    pbl_db_collection.update_one(
        {'type': 'table', 'name': 'teachers'},
        {'$pull': {'data': {'user_id': user_id_str}}}
    )
    pbl_db_collection.update_one(
        {'type': 'table', 'name': 'students'},
        {'$pull': {'data': {'user_id': user_id_str}}}
    )

    if result.modified_count > 0:
        flash("User deleted successfully.")
    else:
        flash("User not found.")

    return redirect(url_for('dashboard.admin_dashboard', action='delete_user_success'))
