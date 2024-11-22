from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import time
from smartcard.System import readers
from smartcard.util import toHexString


#mongodb connect
cluster = "mongodb+srv://sandumagla:QHpB0YxzKyhPLmuw@test.zpzjq.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(cluster, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"MongoDB connection error: {e}")
    exit()

db = client["School_Acces"]
pbl_db = db["pbl_db"]

def read_nfc_card():
    r = readers()
    if len(r) == 0:
        print("No NFC reader detected")
        return None

    reader = r[0]
    connection = reader.createConnection()

    try:
        connection.connect()
        GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        data, sw1, sw2 = connection.transmit(GET_UID)

        if sw1 == 0x90 and sw2 == 0x00:
            return toHexString(data)
        else:
            print("Failed to read card UID.")
            return None
    except Exception as e:
        print(f"NFC reader error: {e}")
        return None

def insert_attendance(uid):
    student_table = pbl_db.find_one({"name": "students"})
    if not student_table or "data" not in student_table:
        print("Students table not found or has no data.")
        return

    student = next((s for s in student_table["data"] if s.get("uid") == uid), None)

    if student:
        new_record = {
            "student_id": student.get("student_id"),
            "user_id": student.get("user_id"),
            "uid": uid,
            "face_id": True,
            "entry_time": datetime.now(),
            "exit_time": None
        }

        result = pbl_db.update_one(
            {"name": "attendance"},
            {"$push": {"data": new_record}}
        )

        if result.modified_count > 0:
            print(f"Attendance recorded for UID {uid}.")
        else:
            print(f"Failed to update attendance for UID {uid}.")
    else:
        print(f"No matching student found for UID {uid}.")

def track_nfc():
    last_uid = None
    last_read_time = 0

    while True:
        uid = read_nfc_card()

        if uid and (uid != last_uid or time.time() - last_read_time > 2):
            print(f"Detected UID: {uid}")
            insert_attendance(uid)
            last_uid = uid
            last_read_time = time.time()
        elif uid:
            print(f"UID {uid} detected, but cooldown is active.")

        time.sleep(0.1)

if __name__ == "__main__":
    try:
        track_nfc()
    except KeyboardInterrupt:
        print("Session ended.")
