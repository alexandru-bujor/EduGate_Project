from flask import Blueprint, request, redirect, url_for, flash, session
from utils.db import get_db_connection

links = Blueprint('links', __name__)

# ------------------ LINK TEACHER TO CLASS ROUTE ------------------
@links.route('/link_teacher_to_class', methods=['POST'])
def link_teacher_to_class():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('auth.login'))

    class_id = request.form['class_id']
    teacher_user_id = request.form['teacher_id']

    # Get MongoDB connection
    db = get_db_connection()
    pbl_db_collection = db['pbl_db']

    # Fetch the teacher record
    teachers_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'teachers'})
    teacher_record = next((t for t in teachers_doc['data'] if str(t['user_id']) == teacher_user_id), None)

    if not teacher_record:
        flash("Teacher not found.")
        return redirect(url_for('dashboard.admin_dashboard'))

    teacher_id = str(teacher_record['teacher_id'])

    # Link the teacher to the class
    result = pbl_db_collection.update_one(
        {'type': 'table', 'name': 'classes', 'data.class_id': class_id},
        {'$set': {'data.$.teacher_id': teacher_id}}
    )

    if result.modified_count > 0:
        flash("Teacher linked to class successfully.")
    else:
        flash("Failed to link teacher to class.")

    return redirect(url_for('dashboard.admin_dashboard', action='link_teacher_to_class_success'))


# ------------------ LINK STUDENT TO CLASS ROUTE ------------------
@links.route('/link_student_class', methods=['POST'])
def link_student_class():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('auth.login'))

    student_id = request.form['student_id']
    class_id = request.form['class_id']

    # Get MongoDB connection
    db = get_db_connection()
    pbl_db_collection = db['pbl_db']

    # Link the student to the class
    result = pbl_db_collection.update_one(
        {'type': 'table', 'name': 'students', 'data.student_id': student_id},
        {'$set': {'data.$.class_id': class_id}}
    )

    if result.modified_count > 0:
        flash("Student linked to class successfully.")
    else:
        flash("Failed to link student to class.")

    return redirect(url_for('dashboard.admin_dashboard', action='link_student_to_class_success'))


# ------------------ LINK STUDENT TO PARENT ROUTE ------------------
@links.route('/link_student_parent', methods=['POST'])
def link_student_parent():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('auth.login'))

    student_id = request.form['student_id']
    parent_id = request.form['parent_id']

    # Get MongoDB connection
    db = get_db_connection()
    pbl_db_collection = db['pbl_db']

    # Link the student to the parent
    result = pbl_db_collection.update_one(
        {'type': 'table', 'name': 'students', 'data.student_id': student_id},
        {'$set': {'data.$.parent_id': parent_id}}
    )

    if result.modified_count > 0:
        flash("Student linked to parent successfully.")
    else:
        flash("Failed to link student to parent.")

    return redirect(url_for('dashboard.admin_dashboard', action='link_student_to_parent_success'))
