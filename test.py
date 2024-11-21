from pymongo import MongoClient

def get_db_connection():
    client = MongoClient(
        "mongodb+srv://sandumagla:QHpB0YxzKyhPLmuw@test.zpzjq.mongodb.net/School_Acces?retryWrites=true&w=majority"
    )
    return client['School_Acces']



def fetch_and_print_uids():
    db = get_db_connection()
    pbl_db_collection = db['pbl_db']

    # Fetch students collection
    students_doc = pbl_db_collection.find_one({'type': 'table', 'name': 'students'})
    if not students_doc:
        print("No students found.")
        return

    students = students_doc.get('data', [])

    # Print UID for each student
    print("UIDs for students:")
    for student in students:
        uid = student.get('uid', "No UID Assigned")
        print(f"Student ID: {student.get('student_id')} - UID: {uid}")


# Run the function
if __name__ == "__main__":
    fetch_and_print_uids()
