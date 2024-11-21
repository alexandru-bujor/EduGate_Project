from flask import Blueprint, jsonify, request
from utils.db import get_db_connection


@app.route('/update_student_uid', methods=['POST'])
def update_student_uid():
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        new_uid = data.get('uid')

        if not student_id:
            return jsonify({'success': False, 'error': 'Student ID is required'}), 400

        db = get_db_connection()
        students_collection = db['pbl_db']

        # Find and update the student document
        result = students_collection.update_one(
            {
                'type': 'table',
                'name': 'students',
                'data': {'$elemMatch': {'student_id': student_id}}
            },
            {
                '$set': {
                    'data.$.uid': new_uid
                }
            }
        )

        if result.modified_count > 0:
            return jsonify({'success': True, 'message': 'UID updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Student not found or UID not changed'}), 404

    except Exception as e:
        print(f"Error updating UID: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500