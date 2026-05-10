// Authentication Module for Elite Academy

class AuthManager {
    constructor() {
        this.currentRole = 'student';
        this.initializeData();
    }

    initializeData() {
        // Initialize with sample data if not exists
        if (!localStorage.getItem('users')) {
            const users = {
                student: [
                    { id: 'STU001', username: 'STU001', password: 'password123', name: 'John Doe', email: 'john.doe@eliteacademy.edu' },
                    { id: 'STU002', username: 'STU002', password: 'password123', name: 'Sarah Johnson', email: 'sarah.johnson@eliteacademy.edu' },
                    { id: 'STU003', username: 'STU003', password: 'password123', name: 'Michael Chen', email: 'michael.chen@eliteacademy.edu' }
                ],
                teacher: [
                    { id: 'TEACH001', username: 'TEACH001', password: 'password123', name: 'Ms. Jennifer Smith', email: 'j.smith@eliteacademy.edu', subject: 'Mathematics' },
                    { id: 'TEACH002', username: 'TEACH002', password: 'password123', name: 'Mr. David Wilson', email: 'd.wilson@eliteacademy.edu', subject: 'Science' },
                    { id: 'TEACH003', username: 'TEACH003', password: 'password123', name: 'Dr. Maria Garcia', email: 'm.garcia@eliteacademy.edu', subject: 'English' }
                ],
                admin: [
                    { id: 'ADMIN001', username: 'ADMIN001', password: 'password123', name: 'Admin User', email: 'admin@eliteacademy.edu' }
                ]
            };
            localStorage.setItem('users', JSON.stringify(users));
        }

        // Initialize marks if not exists
        if (!localStorage.getItem('marks')) {
            const marks = [
                { studentId: 'STU001', studentName: 'John Doe', subject: 'Mathematics', marks: 85, total: 100, date: '2024-05-01' },
                { studentId: 'STU001', studentName: 'John Doe', subject: 'Science', marks: 92, total: 100, date: '2024-05-01' },
                { studentId: 'STU001', studentName: 'John Doe', subject: 'English', marks: 88, total: 100, date: '2024-05-01' },
                { studentId: 'STU002', studentName: 'Sarah Johnson', subject: 'Mathematics', marks: 95, total: 100, date: '2024-05-01' },
                { studentId: 'STU002', studentName: 'Sarah Johnson', subject: 'Science', marks: 89, total: 100, date: '2024-05-01' },
                { studentId: 'STU002', studentName: 'Sarah Johnson', subject: 'English', marks: 91, total: 100, date: '2024-05-01' },
                { studentId: 'STU003', studentName: 'Michael Chen', subject: 'Mathematics', marks: 78, total: 100, date: '2024-05-01' },
                { studentId: 'STU003', studentName: 'Michael Chen', subject: 'Science', marks: 85, total: 100, date: '2024-05-01' },
                { studentId: 'STU003', studentName: 'Michael Chen', subject: 'English', marks: 82, total: 100, date: '2024-05-01' }
            ];
            localStorage.setItem('marks', JSON.stringify(marks));
        }
    }

    login(username, password, role) {
        const users = JSON.parse(localStorage.getItem('users')) || {};
        const userList = users[role] || [];

        const user = userList.find(u => u.username === username && u.password === password);

        if (user) {
            const sessionData = {
                userId: user.id,
                username: user.username,
                name: user.name,
                email: user.email,
                role: role,
                loginTime: new Date().toISOString()
            };

            if (role === 'teacher') {
                sessionData.subject = user.subject;
            }

            localStorage.setItem('currentSession', JSON.stringify(sessionData));
            return { success: true, user: sessionData };
        }

        return { success: false, error: 'Invalid username or password' };
    }

    logout() {
        localStorage.removeItem('currentSession');
    }

    getCurrentSession() {
        const session = localStorage.getItem('currentSession');
        return session ? JSON.parse(session) : null;
    }

    isLoggedIn() {
        return this.getCurrentSession() !== null;
    }

    getStudentMarks(studentId) {
        const marks = JSON.parse(localStorage.getItem('marks')) || [];
        return marks.filter(m => m.studentId === studentId);
    }

    getTeacherStudents(subject) {
        const marks = JSON.parse(localStorage.getItem('marks')) || [];
        const studentsMap = new Map();

        marks.forEach(mark => {
            if (mark.subject === subject) {
                if (!studentsMap.has(mark.studentId)) {
                    studentsMap.set(mark.studentId, {
                        studentId: mark.studentId,
                        studentName: mark.studentName,
                        marks: []
                    });
                }
                studentsMap.get(mark.studentId).marks.push(mark);
            }
        });

        return Array.from(studentsMap.values());
    }

    updateMarks(studentId, subject, marks) {
        const allMarks = JSON.parse(localStorage.getItem('marks')) || [];
        const index = allMarks.findIndex(m => m.studentId === studentId && m.subject === subject);

        if (index !== -1) {
            allMarks[index].marks = marks;
            allMarks[index].date = new Date().toISOString().split('T')[0];
            localStorage.setItem('marks', JSON.stringify(allMarks));
            return true;
        }
        return false;
    }

    getAllUsers() {
        return JSON.parse(localStorage.getItem('users')) || {};
    }

    addUser(role, userData) {
        const users = JSON.parse(localStorage.getItem('users')) || {};
        if (!users[role]) users[role] = [];

        const newUser = {
            id: `${role.toUpperCase()}${Date.now()}`,
            ...userData,
            password: userData.password || 'password123'
        };

        users[role].push(newUser);
        localStorage.setItem('users', JSON.stringify(users));
        return newUser;
    }

    deleteUser(role, userId) {
        const users = JSON.parse(localStorage.getItem('users')) || {};
        if (users[role]) {
            users[role] = users[role].filter(u => u.id !== userId);
            localStorage.setItem('users', JSON.stringify(users));
            return true;
        }
        return false;
    }

    updateUser(role, userId, userData) {
        const users = JSON.parse(localStorage.getItem('users')) || {};
        if (users[role]) {
            const userIndex = users[role].findIndex(u => u.id === userId);
            if (userIndex !== -1) {
                users[role][userIndex] = { ...users[role][userIndex], ...userData };
                localStorage.setItem('users', JSON.stringify(users));
                return true;
            }
        }
        return false;
    }

    getStatistics() {
        const users = this.getAllUsers();
        const marks = JSON.parse(localStorage.getItem('marks')) || [];

        return {
            totalStudents: users.student ? users.student.length : 0,
            totalTeachers: users.teacher ? users.teacher.length : 0,
            totalAdmins: users.admin ? users.admin.length : 0,
            totalMarksRecords: marks.length
        };
    }
}

// Initialize Auth Manager
const authManager = new AuthManager();

// Login handler
function selectRole(role) {
    authManager.currentRole = role;
    document.querySelectorAll('.role-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
}

function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const role = authManager.currentRole;

    const result = authManager.login(username, password, role);

    const errorMsg = document.getElementById('error-message');
    const successMsg = document.getElementById('success-message');

    if (result.success) {
        successMsg.textContent = `Login successful! Welcome, ${result.user.name}`;
        successMsg.style.display = 'block';
        errorMsg.style.display = 'none';

        setTimeout(() => {
            if (role === 'student') {
                window.location.href = 'student-dashboard.html';
            } else if (role === 'teacher') {
                window.location.href = 'teacher-dashboard.html';
            } else if (role === 'admin') {
                window.location.href = 'admin-dashboard.html';
            }
        }, 1500);
    } else {
        errorMsg.textContent = result.error;
        errorMsg.style.display = 'block';
        successMsg.style.display = 'none';
    }
}

// Check authentication on protected pages
function checkAuth(requiredRole) {
    const session = authManager.getCurrentSession();

    if (!session) {
        alert('Please login first');
        window.location.href = 'login.html';
        return false;
    }

    if (requiredRole && session.role !== requiredRole) {
        alert('Unauthorized access');
        window.location.href = 'login.html';
        return false;
    }

    return session;
}

// Logout handler
function handleLogout() {
    authManager.logout();
    alert('Logged out successfully');
    window.location.href = 'login.html';
}

// Update navigation with login/logout
function updateNavigation() {
    const session = authManager.getCurrentSession();
    const navMenu = document.querySelector('.nav-menu');

    if (session) {
        // Add user info and logout
        const userLi = document.createElement('li');
        userLi.innerHTML = `
            <span style="color: var(--secondary-color); margin-right: 20px;">
                👤 ${session.name} (${session.role.charAt(0).toUpperCase() + session.role.slice(1)})
            </span>
            <a href="#" onclick="handleLogout(); return false;">Logout</a>
        `;
        navMenu.appendChild(userLi);

        // Hide login link if visible
        const loginLink = navMenu.querySelector('a[href="login.html"]');
        if (loginLink) {
            loginLink.parentElement.remove();
        }
    } else {
        // Add login link
        const loginLink = navMenu.querySelector('a[href="login.html"]');
        if (!loginLink && !window.location.href.includes('login.html')) {
            const li = document.createElement('li');
            li.innerHTML = '<a href="login.html">Login</a>';
            navMenu.appendChild(li);
        }
    }
}

// Update when DOM is ready
document.addEventListener('DOMContentLoaded', updateNavigation);
