from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# ------------------ DATABASE CONNECTION FUNCTION ------------------
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',  # Your MySQL username
        password='',  # Your MySQL password
        database='school_access'  # Your database name
    )

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

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE phone_number = %s", (phone,))
        user = cursor.fetchone()

        if user and user['password_hash'] == password:  # Consider hashing and checking the password
            session['user_id'] = user['user_id']  # Store user id in session
            session['role'] = user['role']  # Store user role in session

            # Redirect to different dashboards based on role
            if user['role'] == 'Student':
                return redirect(url_for('student_dashboard'))
            elif user['role'] == 'Teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user['role'] == 'Parent':
                return redirect(url_for('parents_dashboard'))
            elif user['role'] == 'Admin':
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid role')
                return redirect(url_for('login'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))

    return render_template('login.html')

# ------------------ STUDENT DASHBOARD ROUTE ------------------
@app.route('/student_dashboard')
def student_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')  # Redirect if user is not logged in

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch student details
    cursor.execute("""
        SELECT u.full_name AS student_name, u.profile_picture
        FROM users u 
        JOIN students s ON u.user_id = s.user_id 
        WHERE u.user_id = %s
    """, (user_id,))
    user = cursor.fetchone()

    # Fetch the parent details of the student
    cursor.execute("""
        SELECT pu.full_name AS parent_name
        FROM students s
        JOIN parents p ON s.parent_id = p.parent_id
        JOIN users pu ON p.user_id = pu.user_id
        WHERE s.user_id = %s
    """, (user_id,))
    parent = cursor.fetchone()

    # Fetch attendance records for the student
    cursor.execute("""
        SELECT a.uid, a.entry_time, a.exit_time, a.face_confirmation 
        FROM attendance a 
        WHERE a.student_id = (SELECT student_id FROM students WHERE user_id = %s) 
        ORDER BY a.entry_time DESC
    """, (user_id,))
    attendance_records = cursor.fetchall()

    conn.close()

    return render_template('student_dashboard.html', user=user, parent=parent, attendance_records=attendance_records)

# ------------------ TEACHER DASHBOARD ROUTE ------------------
@app.route('/teacher_dashboard')
def teacher_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')  # Redirect if user is not logged in

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch teacher details
    cursor.execute("""
        SELECT u.full_name, u.profile_picture
        FROM users u
        JOIN teachers t ON u.user_id = t.user_id
        WHERE u.user_id = %s
    """, (user_id,))
    teacher = cursor.fetchone()

    if not teacher:
        return "Teacher not found or not linked properly."

    # You can add additional data fetching as needed for the teacher

    conn.close()
    return render_template('teacher_dashboard.html', teacher=teacher)



# ------------------ PARENT DASHBOARD ROUTE ------------------
@app.route('/parent_dashboard')
def parents_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch parent details along with parent_id and profile picture
    cursor.execute("""
        SELECT u.*, p.parent_id 
        FROM users u 
        JOIN parents p ON u.user_id = p.user_id 
        WHERE u.user_id = %s
    """, (user_id,))
    parent = cursor.fetchone()

    if not parent:
        return "Parent not found or not linked properly."

    # Fetch students linked to this parent with their profile pictures
    cursor.execute("""
        SELECT 
            s.student_id,
            u.full_name AS student_full_name,
            u.profile_picture AS student_profile_picture,  -- Fetching student's profile picture
            p.parent_id,
            parent_user.full_name AS parent_full_name,
            parent_user.profile_picture AS parent_profile_picture  -- Fetching parent's profile picture
        FROM 
            students s
        JOIN 
            users u ON s.user_id = u.user_id
        JOIN 
            parents p ON s.parent_id = p.parent_id
        JOIN 
            users parent_user ON p.user_id = parent_user.user_id
        WHERE 
            p.parent_id = %s
        ORDER BY 
            s.student_id;
    """, (parent['parent_id'],))
    students = cursor.fetchall()

    # For each student, fetch their attendance history and calculate stats
    for student in students:
        cursor.execute("""
            SELECT a.entry_time, a.exit_time, a.face_confirmation 
            FROM attendance a
            WHERE a.student_id = %s
            ORDER BY a.entry_time DESC
        """, (student['student_id'],))
        attendance_records = cursor.fetchall()

        student['attendance_records'] = attendance_records

        # Initialize attendance stats
        on_time = late = absent = 0
        total_records = len(attendance_records)

        for record in attendance_records:
            entry_time = record['entry_time']
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

    conn.close()
    return render_template('parent_dashboard.html', parent=parent, students=students)


# ------------------ ADMIN DASHBOARD ROUTE ------------------
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))  # Only allow admins to access this page

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch admin details
    cursor.execute("SELECT full_name, profile_picture FROM users WHERE user_id = %s", (user_id,))
    admin = cursor.fetchone()

    # Fetch teachers with their details
    cursor.execute("""
        SELECT u.user_id, u.full_name, u.email, u.phone_number, u.profile_picture
        FROM users u
        JOIN teachers t ON u.user_id = t.user_id
    """)
    teachers = cursor.fetchall()

    # Fetch parents with their details
    cursor.execute("""
        SELECT u.user_id, u.full_name, u.email, u.phone_number, u.profile_picture
        FROM users u
        JOIN parents p ON u.user_id = p.user_id
    """)
    parents = cursor.fetchall()

    # Fetch students with details, including linked parent and class information
    cursor.execute("""
        SELECT s.student_id, s.user_id, u.full_name AS student_name, s.class_id, s.parent_id, u.email, u.phone_number, u.profile_picture,
               c.class_name, c.description AS class_description, pu.full_name AS parent_name
        FROM students s
        JOIN users u ON s.user_id = u.user_id
        LEFT JOIN classes c ON s.class_id = c.class_id
        LEFT JOIN parents p ON s.parent_id = p.parent_id
        LEFT JOIN users pu ON p.user_id = pu.user_id
    """)
    students = cursor.fetchall()

    # Fetch all users for user management
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    # Fetch all classes with linked teacher information
    cursor.execute("""
        SELECT c.class_id, c.class_name, c.description, t.teacher_id, u.full_name AS teacher_name, u.profile_picture AS teacher_picture
        FROM classes c
        LEFT JOIN teachers t ON c.teacher_id = t.teacher_id
        LEFT JOIN users u ON t.user_id = u.user_id
    """)
    classes = cursor.fetchall()

    # Close the connection
    conn.close()

    # Render the template with all the data
    return render_template(
        'admin_dashboard.html',
        admin=admin,
        users=users,
        classes=classes,
        teachers=teachers,
        parents=parents,
        students=students
    )

# ------------------ SEARCH STUDENTS ROUTE ------------------
@app.route('/search_students')
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
@app.route('/search_parents')
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
@app.route('/search_classes')
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

# ------------------ ADD CLASS ROUTE ------------------
@app.route('/add_class', methods=['POST'])
def add_class():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))

    class_name = request.form['class_name']
    description = request.form['description']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO classes (class_name, description) 
        VALUES (%s, %s)
    """, (class_name, description))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Class added successfully!')
    return redirect(url_for('admin_dashboard'))


# ------------------ ADD USER ROUTE ------------------
@app.route('/add_user', methods=['POST'])
def add_user():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))

    full_name = request.form['full_name']
    username = request.form['username']
    password_hash = request.form['password']  # Consider hashing the password
    email = request.form['email']
    phone_number = request.form['phone_number']
    role = request.form['role']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (username, password_hash, full_name, email, phone_number, role) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (username, password_hash, full_name, email, phone_number, role))

    conn.commit()
    cursor.close()
    conn.close()

    flash('User added successfully!')
    return redirect(url_for('admin_dashboard'))

# ------------------ SEARCH TEACHERS ROUTE ------------------
@app.route('/search_teachers')
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


# ------------------ SEARCH USERS ROUTE ------------------
@app.route('/search_users')
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


# ------------------ LINK TEACHER TO CLASS ROUTE ------------------
@app.route('/link_teacher_to_class', methods=['POST'])
def link_teacher_to_class():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))  # Only allow admins to access this page

    class_id = request.form['class_id']
    teacher_user_id = request.form['teacher_id']

    # Establish the database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve the teacher_id from the teachers table using the user_id
    cursor.execute("SELECT teacher_id FROM teachers WHERE user_id = %s", (teacher_user_id,))
    teacher = cursor.fetchone()

    if not teacher:
        flash("Teacher not found.")
        return redirect(url_for('admin_dashboard'))

    teacher_id = teacher[0]

    # Update the class to link the teacher
    try:
        cursor.execute("UPDATE classes SET teacher_id = %s WHERE class_id = %s", (teacher_id, class_id))
        conn.commit()
        flash("Teacher linked to class successfully!")
    except mysql.connector.Error as err:
        flash(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_dashboard'))


# ------------------ LINK STUDENT TO CLASS ROUTE ------------------
@app.route('/link_student_class', methods=['POST'])
def link_student_class():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))

    student_id = request.form['student_id']
    class_id = request.form['class_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE students SET class_id = %s WHERE student_id = %s", (class_id, student_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Student linked to class successfully!')
    return redirect(url_for('admin_dashboard'))

# ------------------ LINK STUDENT TO PARENT ROUTE ------------------
@app.route('/link_student_parent', methods=['POST'])
def link_student_parent():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))

    student_id = request.form['student_id']
    parent_id = request.form['parent_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE students SET parent_id = %s WHERE student_id = %s", (parent_id, student_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Student linked to parent successfully!')
    return redirect(url_for('admin_dashboard'))

# ------------------ DELETE USER ROUTE ------------------
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))

    conn.commit()
    cursor.close()
    conn.close()

    flash('User deleted successfully!')
    return redirect(url_for('admin_dashboard'))

# ------------------ DELETE CLASS ROUTE ------------------
@app.route('/delete_class/<int:class_id>', methods=['POST'])
def delete_class(class_id):
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM classes WHERE class_id = %s", (class_id,))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Class deleted successfully!')
    return redirect(url_for('admin_dashboard'))


# ------------------ RECORD ATTENDANCE ROUTE ------------------
@app.route('/record_attendance', methods=['POST'])
def record_attendance():
    student_id = request.form['student_id']
    entry_time = request.form['entry_time']  # Should include date and time
    exit_time = request.form['exit_time']    # Should include date and time
    face_confirmation = request.form['face_confirmation']  # true/false

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO attendance (student_id, entry_time, exit_time, face_confirmation) 
        VALUES (%s, %s, %s, %s)
    """, (student_id, entry_time, exit_time, face_confirmation))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('admin_dashboard'))

# ------------------ VIEW ATTENDANCE ROUTE ------------------
@app.route('/view_attendance/<int:student_id>', methods=['GET'])
def view_attendance(student_id):
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch attendance records for the given student
    cursor.execute("""
        SELECT student_id, uid, entry_time, exit_time, face_confirmation 
        FROM attendance 
        WHERE student_id = %s
    """, (student_id,))
    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('view_attendance.html', records=records)

# ------------------ LOGOUT ROUTE ------------------
@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
