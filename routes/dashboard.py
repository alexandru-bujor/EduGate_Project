import datetime

from flask import Blueprint, render_template, session, redirect, url_for
from utils.db import get_db_connection

from flask import Blueprint, render_template, session, redirect, url_for, flash
from utils.db import get_db_connection

dashboard_bp = Blueprint('dashboard', __name__)

# ------------------ ADMIN DASHBOARD ROUTE ------------------
@dashboard_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))

    user_id = session['user_id']
    db = get_db_connection()
    pbl_db_collection = db['pbl_db']

    # Fetch admin details
    users_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'users'})
    admin = next((user for user in users_doc['data'] if str(user['user_id']) == user_id), None)

    # Fetch teachers
    teachers_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'teachers'})
    teachers = []
    if teachers_doc:
        for teacher in teachers_doc['data']:
            user = next((u for u in users_doc['data'] if u['user_id'] == teacher['user_id']), {})
            teachers.append({**user, 'teacher_id': teacher.get('teacher_id')})

    # Fetch parents
    parents_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'parents'})
    parents = []
    if parents_doc:
        for parent in parents_doc['data']:
            user = next((u for u in users_doc['data'] if u['user_id'] == parent['user_id']), {})
            parents.append({**user, 'parent_id': parent.get('parent_id')})

    # Fetch students
    students_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'students'})
    classes_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'classes'})
    students = []
    if students_doc:
        for student in students_doc['data']:
            user = next((u for u in users_doc['data'] if u['user_id'] == student['user_id']), {})
            student_class = next((c for c in classes_doc['data'] if c['class_id'] == student.get('class_id')), {})
            parent_user = next((u for u in users_doc['data'] if u['user_id'] == student.get('parent_id')), {})
            students.append({
                'student_id': student.get('student_id'),
                'student_name': user.get('full_name'),
                'class_name': student_class.get('class_name'),
                'parent_name': parent_user.get('full_name'),
                'profile_picture': user.get('profile_picture')
            })

    # Fetch classes
    # Dictionary to map teacher_id to full_name
    teacher_name_mapping = {}
    for teacher in teachers_doc['data']:
        user = next((u for u in users_doc['data'] if u['user_id'] == teacher['user_id']), None)
        if user:
            teacher_name_mapping[teacher['teacher_id']] = user['full_name']

    # Classes list with teacher names
    classes = []
    if classes_doc:
        for class_item in classes_doc['data']:
            teacher_name = teacher_name_mapping.get(class_item.get('teacher_id'), "No Teacher Assigned")
            classes.append({
                'class_id': class_item.get('class_id'),
                'class_name': class_item.get('class_name'),
                'description': class_item.get('description'),
                'teacher_name': teacher_name
            })

    return render_template(
        'admin_dashboard.html',
        admin=admin,
        users=users_doc['data'],
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
        return redirect('/login')

    db = get_db_connection()
    pbl_db_collection = db['pbl_db']

    # Fetch student details
    users_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'users'})
    students_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'students'})
    student = next((s for s in students_doc['data'] if str(s['user_id']) == user_id), None)
    user = next((u for u in users_doc['data'] if str(u['user_id']) == user_id), {})

    # Fetch parent details
    parents_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'parents'})
    parent = next((p for p in parents_doc['data'] if p.get('parent_id') == student.get('parent_id')), {})

    return render_template('student_dashboard.html', user=user, parent=parent)


# ------------------ TEACHER DASHBOARD ROUTE ------------------
@dashboard_bp.route('/teacher_dashboard')
def teacher_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')  # Redirect if user is not logged in

    # Get MongoDB connection
    db = get_db_connection()
    pbl_db_collection = db['pbl_db']

    # Fetch users and teachers data
    users_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'users'})
    teachers_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'teachers'})

    # Find the teacher's details
    teacher_record = next((t for t in teachers_doc['data'] if str(t['user_id']) == user_id), None)
    user_record = next((u for u in users_doc['data'] if str(u['user_id']) == user_id), None)

    if not teacher_record or not user_record:
        flash("Teacher not found or not linked properly.")
        return redirect(url_for('login'))

    # Construct the teacher data for the template
    teacher = {
        'full_name': user_record.get('full_name'),
        'profile_picture': user_record.get('profile_picture'),
    }

    return render_template('teacher_dashboard.html', teacher=teacher)


# ------------------ PARENT DASHBOARD ROUTE ------------------

@dashboard_bp.route('/parent_dashboard')
def parent_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    # Get MongoDB connection
    db = get_db_connection()
    pbl_db_collection = db['pbl_db']

    # Fetch users, parents, students, and attendance data
    users_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'users'})
    parents_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'parents'})
    students_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'students'})
    attendance_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'attendance'})

    # Find the parent record based on user_id
    parent_record = next((p for p in parents_doc['data'] if str(p['user_id']) == user_id), None)
    parent_user = next((u for u in users_doc['data'] if str(u['user_id']) == user_id), None)

    if not parent_record or not parent_user:
        flash("Parent not found or not linked properly.")
        return redirect(url_for('login'))

    # Construct the parent data for the template
    parent = {
        'full_name': parent_user.get('full_name'),
        'profile_picture': parent_user.get('profile_picture'),
        'parent_id': parent_record.get('parent_id'),
    }

    # Fetch students linked to this parent
    students = []
    for student in students_doc['data']:
        if student.get('parent_id') == parent['parent_id']:
            student_user = next((u for u in users_doc['data'] if u['user_id'] == student['user_id']), {})
            students.append({
                'student_id': student.get('student_id'),
                'student_full_name': student_user.get('full_name'),
                'student_profile_picture': student_user.get('profile_picture')
            })

    # Fetch attendance records and calculate stats for each student
    for student in students:
        student_id = student['student_id']
        attendance_records = [
            record for record in attendance_doc['data'] if record.get('student_id') == student_id
        ]

        student['attendance_records'] = attendance_records

        # Initialize attendance stats
        on_time = late = absent = 0
        total_records = len(attendance_records)

        for record in attendance_records:
            entry_time = record.get('entry_time')
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

    return render_template('parent_dashboard.html', parent=parent, students=students)
