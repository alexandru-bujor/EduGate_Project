from flask import Blueprint, request, redirect, url_for, session, flash
from utils.db import get_db_connection

class_management_bp = Blueprint('class_management', __name__)

# ------------------ ADD CLASS ROUTE ------------------
@class_management_bp.route('/add_class', methods=['POST'])
def add_class():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('auth.login'))

    class_name = request.form['class_name']
    description = request.form['description']

    db = get_db_connection()
    pbl_db_collection = db['pbl_db']

    # Fetch the classes document
    classes_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'classes'})

    if not classes_doc:
        flash("Classes document not found.")
        return redirect(url_for('dashboard.admin_dashboard'))

    # Generate a new class ID (convert to int before comparison)
    class_id = max([int(c.get('class_id', 0)) for c in classes_doc['data']], default=0) + 1

    # Create the new class record
    new_class = {
        'class_id': str(class_id),  # Store as a string for consistency
        'class_name': class_name,
        'description': description
    }

    # Add the new class to the data array
    pbl_db_collection.update_one(
        {'type': 'table', 'name': 'classes'},
        {'$push': {'data': new_class}}
    )

    flash("Class added successfully.")
    return redirect(url_for('dashboard.admin_dashboard', action='add_class_success'))

# ------------------ DELETE CLASS ROUTE ------------------
@class_management_bp.route('/delete_class/<int:class_id>', methods=['POST'])
def delete_class(class_id):
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('auth.login'))

    # Get MongoDB connection
    db = get_db_connection()
    pbl_db_collection = db['pbl_db']

    # Convert `class_id` to string for the query
    class_id_str = str(class_id)

    # Attempt to delete the class from the data array
    result = pbl_db_collection.update_one(
        {'type': 'table', 'name': 'classes'},
        {'$pull': {'data': {'class_id': class_id_str}}}
    )

    # Check if the class was successfully deleted
    if result.modified_count > 0:
        flash("Class deleted successfully.")
    else:
        flash("Class not found.")

    return redirect(url_for('dashboard.admin_dashboard', action='delete_class_success'))
