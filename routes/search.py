from flask import Blueprint, jsonify, request
from utils.db import get_db_connection

search = Blueprint('search', __name__)

# ------------------ SEARCH USERS ROUTE ------------------
@search.route('/search_users')
def search_users():
    query = request.args.get('query', '').strip()  # Remove leading/trailing whitespace
    db = get_db_connection()
    users_doc = db['pbl_db'].find_one({'type': 'table', 'name': 'users'})

    if not users_doc:
        return jsonify([])

    # Use MongoDB regex for partial matching with case-insensitivity
    regex_query = {'$regex': query, '$options': 'i'}
    users = []

    for user in users_doc['data']:
        full_name = user.get('full_name', '').strip()
        email = user.get('email', '')
        username = user.get('username', '')

        # Case-insensitive search using $regex with 'i' option
        if (regex_query['$regex'].lower() in full_name.lower() or
            regex_query['$regex'].lower() in email.lower() or
            regex_query['$regex'].lower() in username.lower()):
            users.append({
                'user_id': user.get('user_id'),
                'full_name': full_name,
                'username': username,
                'email': email,
                'phone_number': user.get('phone_number'),
                'role': user.get('role'),
                'profile_picture': user.get('profile_picture')
            })

    return jsonify(users)




# ------------------ SEARCH STUDENTS ROUTE ------------------
@search.route('/search_students')
def search_students():
    query = request.args.get('query', '').strip()  # Remove leading/trailing whitespace
    db = get_db_connection()
    users_doc = db['pbl_db'].find_one({'type': 'table', 'name': 'users'})
    students_doc = db['pbl_db'].find_one({'type': 'table', 'name': 'students'})
    classes_doc = db['pbl_db'].find_one({'type': 'table', 'name': 'classes'})
    parents_doc = db['pbl_db'].find_one({'type': 'table', 'name': 'parents'})

    if not (users_doc and students_doc):
        return jsonify([])

    query_lower = query.lower()
    students = []

    for student in students_doc['data']:
        user = next((u for u in users_doc['data'] if u['user_id'] == student['user_id']), {})
        class_info = next((c for c in classes_doc['data'] if c['class_id'] == student.get('class_id')), {})
        parent = next((p for p in parents_doc['data'] if p['parent_id'] == student.get('parent_id')), {})
        parent_user = next((u for u in users_doc['data'] if u['user_id'] == parent.get('user_id')), {})

        # Extract fields and strip whitespace
        full_name = user.get('full_name', '').strip()
        username = user.get('username', '').strip()
        email = user.get('email', '').strip()

        # Perform case-insensitive search
        if (query_lower in full_name.lower() or
            query_lower in username.lower() or
            query_lower in email.lower()):
            students.append({
                'student_id': student['student_id'],
                'username': username,
                'student_name': full_name,
                'email': email,
                'profile_picture': user.get('profile_picture'),
                'class_name': class_info.get('class_name'),
                'parent_name': parent_user.get('full_name')
            })

    return jsonify(students)


# ------------------ SEARCH PARENTS ROUTE ------------------
@search.route('/search_parents')
def search_parents():
    query = request.args.get('query', '').strip()  # Remove leading/trailing whitespace
    db = get_db_connection()
    users_doc = db['pbl_db'].find_one({'type': 'table', 'name': 'users'})
    parents_doc = db['pbl_db'].find_one({'type': 'table', 'name': 'parents'})

    if not (users_doc and parents_doc):
        return jsonify([])

    query_lower = query.lower()
    parents = []

    for parent in parents_doc['data']:
        user = next((u for u in users_doc['data'] if u['user_id'] == parent['user_id']), {})

        # Extract fields and strip whitespace
        full_name = user.get('full_name', '').strip()
        email = user.get('email', '').strip()

        # Perform case-insensitive search
        if (query_lower in full_name.lower() or
            query_lower in email.lower()):
            parents.append({
                'user_id': user.get('user_id'),
                'full_name': full_name,
                'email': email,
                'phone_number': user.get('phone_number'),
                'profile_picture': user.get('profile_picture')
            })

    return jsonify(parents)



# ------------------ SEARCH CLASSES ROUTE ------------------
@search.route('/search_classes')
def search_classes():
    query = request.args.get('query', '')
    db = get_db_connection()
    classes_doc = db['pbl_db'].find_one({'type': 'table', 'name': 'classes'})

    if not classes_doc:
        return jsonify([])

    regex_query = {'$regex': query, '$options': 'i'}
    classes = [
        c for c in classes_doc['data']
        if (regex_query['$regex'] in c.get('class_name', '') or
            regex_query['$regex'] in c.get('description', ''))
    ]

    return jsonify(classes)


# ------------------ SEARCH TEACHERS ROUTE ------------------
@search.route('/search_teachers')
def search_teachers():
    query = request.args.get('query', '').strip()  # Remove leading/trailing whitespace
    db = get_db_connection()
    users_doc = db['pbl_db'].find_one({'type': 'table', 'name': 'users'})
    teachers_doc = db['pbl_db'].find_one({'type': 'table', 'name': 'teachers'})

    if not (users_doc and teachers_doc):
        return jsonify([])

    query_lower = query.lower()
    teachers = []

    for teacher in teachers_doc['data']:
        user = next((u for u in users_doc['data'] if u['user_id'] == teacher['user_id']), {})

        # Extract fields and strip whitespace
        full_name = user.get('full_name', '').strip()
        email = user.get('email', '').strip()

        # Perform case-insensitive search
        if (query_lower in full_name.lower() or
            query_lower in email.lower()):
            teachers.append({
                'user_id': user.get('user_id'),
                'full_name': full_name,
                'email': email,
                'phone_number': user.get('phone_number'),
                'profile_picture': user.get('profile_picture')
            })

    return jsonify(teachers)
