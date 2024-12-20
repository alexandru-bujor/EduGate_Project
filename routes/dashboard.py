import datetime

from flask import Blueprint, render_template, session,  request, flash, redirect, url_for
from utils.db import get_db_connection
from routes.user_management import verify_password, hash_password


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
                'uid': student.get('uid', 'No UID Assigned'),  # Default to "No UID Assigned"
                'profile_picture': user.get('profile_picture')
            })

    teacher_name_mapping = {}
    for teacher in teachers_doc['data']:
        user = next((u for u in users_doc['data'] if u['user_id'] == teacher['user_id']), None)
        if user:
            teacher_name_mapping[teacher['teacher_id']] = user['full_name']

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
        user = admin,
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
    attendance_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'attendance'})
    student_record = next((s for s in students_doc['data'] if str(s['user_id']) == user_id), None)
    student_user = next((u for u in users_doc['data'] if str(u['user_id']) == user_id), None)

    if not student_record or not student_user:
        flash("Student not found or not linked properly.")
        return redirect(url_for('login'))


    student = {
        'student_id': student_record.get('student_id'),
        'username': student_user.get('username'),
        'full_name': student_user.get('full_name'),
        'email': student_user.get('email'),
        'profile_picture': student_user.get('profile_picture')
    }

    # Fetch parent details
    # parents_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'parents'})
    # parent = next((p for p in parents_doc['data'] if p.get('parent_id') == student.get('parent_id')), {})

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

    return render_template('student_dashboard.html', student=student, user=student
                           # ,parent=parent
         )


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
    classes_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'classes'})
    students_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'students'})
    parents_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'parents'})
    attendance_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'attendance'})

    teacher_record = next((t for t in teachers_doc['data'] if str(t['user_id']) == user_id), None)
    teacher_user = next((u for u in users_doc['data'] if str(u['user_id']) == user_id), None)

    if not teacher_record or not teacher_user:
        flash("Teacher not found or not linked properly.")
        return redirect(url_for('login'))

    # Construct the teacher data for the template
    teacher = {
        'full_name': teacher_user.get('full_name'),
        'profile_picture': teacher_user.get('profile_picture'),
        'teacher_id': teacher_record.get('teacher_id'),
    }

    # Classes list
    classes = []
    for class_item in classes_doc['data']:
        if class_item.get('teacher_id') == teacher['teacher_id']:
            classes.append({
                'class_id': class_item.get('class_id'),
                'class_name': class_item.get('class_name'),
                'description': class_item.get('description'),
                'teacher_id': class_item.get('teacher_id')
            })

    # Fetch students linked to this parent
    students = []
    for class_item in classes:
        for student in students_doc['data']:
            if student.get('class_id') == class_item['class_id']:
               student_user = next((u for u in users_doc['data'] if u['user_id'] == student['user_id']), {})
               students.append({
                    'student_id': student.get('student_id'),
                    'student_username': student_user.get('username'),
                    'student_full_name': student_user.get('full_name'),
                    'student_email': student_user.get('email'),
                    'student_profile_picture': student_user.get('profile_picture')
                })




    # Fetch parents
    # parents = []
    # for student in students:
    # for parent in parents_doc['data']:
    #     if parent.get('parent_id')  == student['parent_id']:
    #         parent_user = next((u for u in users_doc['data'] if u['user_id'] == parent['user_id']), {})
    #     parents.append({
    #         'parent_id': parent.get('parent_id'),
    #         'parent_full_name': parent_user.get('full_name'),
    #         'parent_profile_picture': parent_user.get('profile_picture')
    #     })





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


    return render_template('teacher_dashboard.html',
                           teacher=teacher,
                           # parents=parents,
                           user = teacher,
                           classes=classes,
                           students=students)



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

    return render_template('parent_dashboard.html', parent=parent, user=parent, students=students)


@dashboard_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    user_id = session.get('user_id')

    db = get_db_connection()
    pbl_db_collection = db['pbl_db']

    users_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'users'})
    user = next((u for u in users_doc['data'] if u.get('user_id') == user_id), None)

    if request.method == 'POST':
        current_password = request.form['current']
        confirm_current = request.form['confirm-curr']
        new_password = request.form['new']
        confirm_new = request.form['confirm-new']

        password_match = verify_password(user['password_hash'], current_password)

        if password_match and current_password == confirm_current:
            if new_password == confirm_new:
                if new_password == current_password:
                    flash("Please enter something different from your current password.")
                    return render_template('/settings.html', user=user, action="Same password!")
                else:
                    new_password_hash = hash_password(new_password)

                    result = pbl_db_collection.update_one(
                        {'type': 'table', 'name': 'users', 'data.user_id': user_id},
                        {'$set': {'data.$.password_hash': new_password_hash}}
                    )

                    flash('Password updated successfully.')
                    return render_template('/settings.html', user=user, action="Successful change!")

            else:
                flash("New passwords don't match.")
                return render_template('/settings.html', user=user, action="New passwords don't match!")

        else:
            flash("Current password is incorrect or doesn't match the confirmation.")
            return render_template('/settings.html', user=user, action="Current password is incorrect or doesn't match the confirmation!")

    return render_template('/settings.html', user=user)
