# Changelog

FAF EduGate PBL Project.

## [1.1.0] - 2024-11-08
### Added
- `nfc.py` created the nfc attendence code for registering information in MongoDB.
- Password encrypting algorithm
- Attach a card UID to a student and add to admin dashboard an option to change student's UID.
- Change face recognition script so it would get profile photos locally and write attendance records to MongoDB
- More design changes in Parent Dashboard
- Add links to homepage from each dashboard
- Create a figma model for adding users
- Implement the back-end on teacher dashboard
- Telegram bot performs a log in as a parent using the password and username
### Fixed
-  Fix rendering student_dashboard
- Fix design detail (add some margins) in parent dashboard
- Fixed the base connection for the nfc with Mongo DB


## [1.0.1] - 2024-11-08
### Added
- `CHANGELOG.md` file created to document changes.

### Fixed
- Logic for linking teachers and parents in the class and student sections.
- Problems with displaying info from database records.
- CSS errors on main page.
- Improved design for all pages (Student, Parent, Admin Dashboards)
- Switched to a Cloud Database using MongoDB and connected with Backend

## [1.0.0] - 2024-10-01
### Initially Created
- Front-end: Figma design, building front from mockups.
- Back-end: Server part, NFC reader, FaceRecognition part.
- Local Database: System architecture design.
