from utils.db import get_db_connection

class User:
    @staticmethod
    def get_user_by_id(user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
