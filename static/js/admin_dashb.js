// ------------------ SUCCESS MESSAGES HANDLING ------------------
function showAlertForAction() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('action')) {
        const action = urlParams.get('action');
        let message = "";

        // Define messages for each action
        switch (action) {
            case 'add_user_success':
                message = "User added successfully!";
                break;
            case 'delete_user_success':
                message = "User deleted successfully!";
                break;
            case 'add_class_success':
                message = "Class added successfully!";
                break;
            case 'delete_class_success':
                message = "Class deleted successfully!";
                break;
            case 'link_teacher_to_class_success':
                message = "Teacher linked to class successfully!";
                break;
            case 'link_student_to_class_success':
                message = "Student linked to class successfully!";
                break;
            case 'link_student_to_parent_success':
                message = "Student linked to parent successfully!";
                break;
            default:
                message = "";
        }

        if (message) {
            alert(message);
        }
    }
}



// ------------------ FOOTER LOADING ------------------
function loadFooter() {
    fetch('footer.html')
        .then(response => response.text())
        .then(data => document.getElementById('footer-container').innerHTML = data)
        .catch(error => console.error("Error loading footer:", error));
}



// ------------------ SECTION DISPLAY MANAGEMENT ------------------
function showSection(sectionId) {
    document.querySelectorAll("section").forEach((section) => section.classList.remove("active"));
    document.querySelectorAll("nav a").forEach((link) => link.classList.remove("active"));
    document.getElementById(sectionId).classList.add("active");
    document.getElementById("nav-" + sectionId).classList.add("active");

    switch (sectionId) {
        case "users": searchUsers(); break;
        case "classes": searchClasses(); break;
        case "teachers": searchTeachers(); break;
        case "parents": searchParents(); break;
        case "students": searchStudents(); break;
    }
}



// ------------------ USER MANAGEMENT ------------------
function searchUsers() {
    const query = document.getElementById("user-search-query").value;
    fetch(`/search/search_users?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(users => renderUserTable(users))
        .catch(error => console.error("Error fetching users:", error));
}

function renderUserTable(users) {
    const usersTableBody = document.querySelector("#users-table tbody");
    usersTableBody.innerHTML = "";
    users.forEach(user => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td><img src="/static/profile_pictures/${user.profile_picture || 'default.jpg'}" width="50" height="50"></td>
            <td>${user.full_name}</td>
            <td>${user.username}</td>
            <td>${user.email}</td>
            <td>${user.phone_number}</td>
            <td>${user.role}</td>
            <td><button onclick="deleteUser(${user.user_id})">Delete</button></td>
        `;
        usersTableBody.appendChild(row);
    });
}

function deleteUser(userId) {
    if (confirm("Are you sure you want to delete this user?")) {
        fetch(`/user_management/delete_user/${userId}`, {
            method: "POST",
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || data.error);
            searchUsers();
        })
        .catch(error => console.error("Error:", error));
    }
}



// ------------------ CLASS MANAGEMENT ------------------
function searchClasses() {
    const query = document.getElementById("class-search-query").value;
    fetch(`/search/search_classes?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(classes => renderClassTable(classes))
        .catch(error => console.error("Error fetching classes:", error));
}

function renderClassTable(classes) {
    const classesTableBody = document.querySelector("#classes-table tbody");
    classesTableBody.innerHTML = "";
    classes.forEach(classData => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${classData.class_id}</td>
            <td>${classData.class_name}</td>
            <td>${classData.description}</td>
            <td><button onclick="deleteClass(${classData.class_id})">Delete</button></td>
        `;
        classesTableBody.appendChild(row);
    });
}

function deleteClass(classId) {
    if (confirm("Are you sure you want to delete this class?")) {
        fetch(`/class_management/delete_class/${classId}`, { method: "DELETE" })
            .then(response => response.json())
            .then(data => {
                alert(data.message || data.error);
                searchClasses();
            })
            .catch(error => console.error("Error deleting class:", error));
    }
}



// ------------------ TEACHER MANAGEMENT ------------------
function searchTeachers() {
    const query = document.getElementById("teacher-search-query").value;
    fetch(`/search/search_teachers?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(teachers => renderTeacherTable(teachers))
        .catch(error => console.error("Error fetching teachers:", error));
}

function renderTeacherTable(teachers) {
    const teachersTableBody = document.getElementById("teachers-table").getElementsByTagName("tbody")[0];
    teachersTableBody.innerHTML = "";
    teachers.forEach(teacher => {
        const profilePictureUrl = teacher.profile_picture
            ? `/static/profile_pictures/${teacher.profile_picture}`
            : "/static/profile_pictures/default.jpg";
        const row = document.createElement("tr");
        row.innerHTML = `
            <td><img src="${profilePictureUrl}" width="50" height="50"></td>
            <td>${teacher.full_name}</td>
            <td>${teacher.email}</td>
            <td>${teacher.phone_number}</td>
            <td><button onclick="deleteTeacher(${teacher.user_id})">Delete</button></td>
        `;
        teachersTableBody.appendChild(row);
    });
}

function deleteTeacher(teacherId) {
    if (confirm("Are you sure you want to delete this teacher?")) {
        fetch(`/user_management/delete_user/${teacherId}`, { method: "DELETE" })
            .then(response => response.json())
            .then(data => {
                alert(data.message || data.error);
                searchTeachers();
            })
            .catch(error => console.error("Error deleting teacher:", error));
    }
}

function searchTeacher(teacherName) {
        // Switch to the Teachers section
        showSection('teachers');

        // Set the search query for teachers and perform the search
        document.getElementById('teacher-search-query').value = teacherName;
        searchTeachers();
}



// ------------------ PARENT MANAGEMENT ------------------
function searchParents() {
    const query = document.getElementById("parent-search-query").value;
    fetch(`/search/search_parents?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(parents => renderParentTable(parents))
        .catch(error => console.error("Error fetching parents:", error));
}

function renderParentTable(parents) {
    const parentsTableBody = document.querySelector("#parents-table tbody");
    parentsTableBody.innerHTML = "";
    parents.forEach(parent => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td><img src="/static/profile_pictures/${parent.profile_picture || 'default.jpg'}" width="50" height="50"></td>
            <td>${parent.full_name}</td>
            <td>${parent.email}</td>
            <td>${parent.phone_number}</td>
            <td><button onclick="deleteParent(${parent.user_id})">Delete</button></td>
        `;
        parentsTableBody.appendChild(row);
    });
}

function deleteParent(parentId) {
    if (confirm("Are you sure you want to delete this parent?")) {
        fetch(`/user_management/delete_user/${parentId}`, { method: "DELETE" })
            .then(response => response.json())
            .then(data => {
                alert(data.message || data.error);
                searchParents();
            })
            .catch(error => console.error("Error deleting parent:", error));
    }
}

function searchParent(parentName) {
    // Switch to the Parents section
    showSection('parents');

    // Set the search query for parents and perform the search
    document.getElementById('parent-search-query').value = parentName;
    searchParents();
}



// ------------------ STUDENT MANAGEMENT ------------------
function searchStudents() {
    const query = document.getElementById("student-search-query").value;
    fetch(`/search/search_students?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(students => renderStudentTable(students))
        .catch(error => console.error("Error fetching students:", error));
}

function renderStudentTable(students) {
    const studentsTableBody = document.getElementById("students-table").getElementsByTagName("tbody")[0];
    studentsTableBody.innerHTML = "";
    students.forEach(student => {
        const profilePictureUrl = student.profile_picture
            ? `/static/profile_pictures/${student.profile_picture}`
            : "/static/profile_pictures/default.jpg";
        const row = document.createElement("tr");
        row.innerHTML = `
            <td><img src="${profilePictureUrl}" width="60" height="60"></td>
            <td>${student.username}</td>
            <td>${student.student_name}</td>
            <td>${student.class_name || "No Class Assigned"}</td>
            <td>${student.email}</td>
            <td>${student.parent_name ? `<a href="#" onclick="searchParent('${student.parent_name}')">${student.parent_name}</a>` : "No Parent Assigned"}</td>
        `;
        studentsTableBody.appendChild(row);
    });
}


document.addEventListener("DOMContentLoaded", () => {
    loadFooter();
    searchUsers();
    searchClasses();
    searchTeachers();
    searchParents();
    searchStudents();
    showAlertForAction();
});