from flask import Blueprint, jsonify, request
from utils.db import get_db_connection

search = Blueprint('search', __name__)


# ------------------ SEARCH USERS ROUTE ------------------
@search.route('/search_users')
def search_users():
    query = request.args.get('query', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Use LIKE with wildcard for partial matching
    cursor.execute("""
        SELECT user_id, full_name, email, phone_number, role, profile_picture 
        FROM users 
        WHERE full_name LIKE %s OR email LIKE %s OR username LIKE %s
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))
    users = cursor.fetchall()

    conn.close()
    return jsonify(users)


# ------------------ SEARCH STUDENTS ROUTE ------------------
@search.route('/search_students')
def search_students():
    query = request.args.get('query', '')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Modify the query to include username and profile picture
    cursor.execute("""
        SELECT s.student_id, u.username, u.full_name AS student_name, u.email, u.profile_picture, 
               c.class_name, pu.full_name AS parent_name, p.parent_id
        FROM students s
        JOIN users u ON s.user_id = u.user_id
        LEFT JOIN classes c ON s.class_id = c.class_id
        LEFT JOIN parents p ON s.parent_id = p.parent_id
        LEFT JOIN users pu ON p.user_id = pu.user_id
        WHERE u.full_name LIKE %s OR u.username LIKE %s
    """, (f"%{query}%", f"%{query}%"))

    students = cursor.fetchall()
    conn.close()

    return jsonify(students)


# ------------------ SEARCH PARENTS ROUTE ------------------
@search.route('/search_parents')
def search_parents():
    query = request.args.get('query', '')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Search parents by name or email
    cursor.execute("""
        SELECT u.user_id, u.full_name, u.email, u.phone_number, u.profile_picture
        FROM users u
        JOIN parents p ON u.user_id = p.user_id
        WHERE u.full_name LIKE %s OR u.email LIKE %s
    """, (f"%{query}%", f"%{query}%"))

    parents = cursor.fetchall()

    conn.close()

    return jsonify(parents)


# ------------------ SEARCH CLASSES ROUTE ------------------
@search.route('/search_classes')
def search_classes():
    query = request.args.get('query', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Use LIKE with wildcard for partial matching
    cursor.execute("""
        SELECT class_id, class_name, description 
        FROM classes 
        WHERE class_name LIKE %s OR description LIKE %s
    """, (f"%{query}%", f"%{query}%"))
    classes = cursor.fetchall()

    conn.close()
    return jsonify(classes)


# ------------------ SEARCH TEACHERS ROUTE ------------------
@search.route('/search_teachers')
def search_teachers():
    query = request.args.get('query', '')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Search teachers by name or email
    cursor.execute("""
        SELECT u.user_id, u.full_name, u.email, u.phone_number, u.profile_picture
        FROM users u
        JOIN teachers t ON u.user_id = t.user_id
        WHERE u.full_name LIKE %s OR u.email LIKE %s
    """, (f"%{query}%", f"%{query}%"))

    teachers = cursor.fetchall()

    conn.close()

    return jsonify(teachers)

