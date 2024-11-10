from flask import Blueprint, request, redirect, url_for, session, flash
from utils.db import get_db_connection

class_management_bp = Blueprint('class_management', __name__)

@class_management_bp.route('/add_class', methods=['POST'])
def add_class():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('auth.login'))

    class_name = request.form['class_name']
    description = request.form['description']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO classes (class_name, description) VALUES (%s, %s)", (class_name, description))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('dashboard.admin_dashboard', action='add_class_success'))

@class_management_bp.route('/delete_class/<int:class_id>', methods=['POST'])
def delete_class(class_id):
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM classes WHERE class_id = %s", (class_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('dashboard.admin_dashboard', action='delete_class_success'))
