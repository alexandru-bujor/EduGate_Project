import time
import cv2
import face_recognition
from utils.db import get_db_connection

# Load known faces and student IDs
def load_known_faces():
    db = get_db_connection()
    users_collection = db['pbl_db']

    # Fetch students with profile pictures
    students_doc = users_collection.find_one({'type': 'table', 'name': 'students'})
    users_doc = users_collection.find_one({'type': 'table', 'name': 'users'})

    known_faces = []
    student_ids = []

    if students_doc and users_doc:
        for student in students_doc['data']:
            user = next((u for u in users_doc['data'] if u['user_id'] == student['user_id']), None)
            if user and user.get('profile_picture'):
                image_path = f"static/profile_pictures/{user['profile_picture']}"
                try:
                    image = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        known_faces.append(encodings[0])
                        student_ids.append(student['student_id'])
                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")

    return known_faces, student_ids


# Initialize known faces and student IDs
known_face_encodings, known_student_ids = load_known_faces()

# Load OpenCV's Haar Cascade for faster face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize camera
video_capture = cv2.VideoCapture(0)

# Set the resolution to lower to increase FPS
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Initialize the time for the delay
last_recognition_time = time.time()

print("Starting live face recognition... Press 'q' to quit.")

while True:
    # Capture a frame from the video feed
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Check if 1 second has passed since the last recognition
    current_time = time.time()
    if current_time - last_recognition_time >= 1:
        # Update the last recognition time
        last_recognition_time = current_time

        # Convert the frame to grayscale (needed for Haar Cascade)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces using Haar Cascade
        face_locations = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # For each face detected, find the face encoding and compare it with known encodings
        for (x, y, w, h) in face_locations:
            # Convert the face bounding box into the format expected by face_recognition (top, right, bottom, left)
            top, right, bottom, left = y, x + w, y + h, x

            # Get the face encoding for this detected face
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_encodings = face_recognition.face_encodings(rgb_frame, [(top, right, bottom, left)])

            if len(face_encodings) > 0:
                face_encoding = face_encodings[0]

                # Compare this encoding with the known encodings
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

                best_match_index = None if len(face_distances) == 0 else face_distances.argmin()

                if matches[best_match_index]:
                    student_id = known_student_ids[best_match_index]
                    print(f"Recognized student ID: {student_id}")

                    # Check the latest attendance record for this student
                    db = get_db_connection()
                    attendance_collection = db['attendance_records']

                    # TODO when the "attach card UID to student" and nfc.py will be implemented make so it would update the base 0 value on face_recognition_status"
                    # # Retrieve the most recent attendance record for this student where face_confirmed is False
                    # record = attendance_collection.find_one(
                    #     {"student_id": student_id, "face_confirmed": 0, "status": "active"},
                    #     sort=[("entry_time", -1)]
                    # )
                    #
                    # if record:
                    #     # Update the face_confirmed to 1
                    #     attendance_collection.update_one(
                    #         {"_id": record["_id"]},
                    #         {"$set": {"face_confirmed": 1}}
                    #     )
                    #     print(f"Updated face confirmation for student ID: {student_id}")

            # Draw a rectangle around the face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the video feed with rectangles around detected faces
    cv2.imshow("Live Face Recognition", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
video_capture.release()
cv2.destroyAllWindows()
