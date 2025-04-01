// Main application JavaScript for the Fingerprint Attendance System

// Initialize navigation and form handlers once the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initFormHandlers();
});

// Setup navigation between different sections
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the target page
            const targetPage = this.getAttribute('data-page');
            
            // Remove active class from all links and sections
            navLinks.forEach(l => l.classList.remove('active'));
            document.querySelectorAll('.page-section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Add active class to clicked link and corresponding section
            this.classList.add('active');
            document.getElementById(targetPage).classList.add('active');
        });
    });
}

// Initialize all form handlers and UI interactions
function initFormHandlers() {
    // Class form handlers
    document.getElementById('add-class-btn')?.addEventListener('click', function() {
        document.getElementById('class-form-container').style.display = 'block';
        document.getElementById('class-form').reset();
        document.getElementById('class-id').value = '';
        document.getElementById('schedules-container').innerHTML = '';
        addScheduleItem(); // Add at least one schedule item
    });
    
    document.getElementById('cancel-class')?.addEventListener('click', function() {
        document.getElementById('class-form-container').style.display = 'none';
    });
    
    document.getElementById('add-schedule')?.addEventListener('click', function(e) {
        e.preventDefault();
        addScheduleItem();
    });
    
    document.getElementById('class-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        saveClass();
    });
    
    // Student form handlers
    document.getElementById('add-student-btn')?.addEventListener('click', function() {
        document.getElementById('student-form-container').style.display = 'block';
        document.getElementById('student-form').reset();
        document.getElementById('student-id').value = '';
    });
    
    document.getElementById('cancel-student')?.addEventListener('click', function() {
        document.getElementById('student-form-container').style.display = 'none';
    });
    
    document.getElementById('student-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        saveStudent();
    });
    
    // Attendance form handler
    document.getElementById('attendance-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        saveAttendance();
    });
    
    // Report form handlers
    document.getElementById('class-report-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        generateClassReport();
    });
    
    document.getElementById('student-report-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        generateStudentReport();
    });
    
    // Load initial data for select dropdowns
    loadClassesData();
    loadStudentsData();
    
    // Set current date and time for attendance form
    const now = new Date();
    const dateTimeString = now.toISOString().slice(0, 16);
    const attendanceTimestamp = document.getElementById('attendance-timestamp');
    if (attendanceTimestamp) {
        attendanceTimestamp.value = dateTimeString;
    }
    
    // Set current date for report form
    const today = now.toISOString().slice(0, 10);
    const reportDate = document.getElementById('report-date');
    if (reportDate) {
        reportDate.value = today;
    }
}

// Add a new schedule item to the class form
function addScheduleItem() {
    const container = document.getElementById('schedules-container');
    const scheduleIndex = container.children.length;
    
    const scheduleItem = document.createElement('div');
    scheduleItem.classList.add('schedule-item');
    
    scheduleItem.innerHTML = `
        <select name="day_of_week_${scheduleIndex}" required>
            <option value="">Select Day</option>
            <option value="Monday">Monday</option>
            <option value="Tuesday">Tuesday</option>
            <option value="Wednesday">Wednesday</option>
            <option value="Thursday">Thursday</option>
            <option value="Friday">Friday</option>
            <option value="Saturday">Saturday</option>
            <option value="Sunday">Sunday</option>
        </select>
        <input type="time" name="start_time_${scheduleIndex}" required placeholder="Start Time">
        <input type="time" name="end_time_${scheduleIndex}" required placeholder="End Time">
        <input type="text" name="room_number_${scheduleIndex}" required placeholder="Room Number">
        <button type="button" class="remove-schedule" onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(scheduleItem);
}

// Save class data
async function saveClass() {
    try {
        // Get form data
        const classId = document.getElementById('class-id').value;
        const className = document.getElementById('class-name').value;
        const lecturer = document.getElementById('lecturer').value;
        
        // Get schedules
        const scheduleItems = document.querySelectorAll('.schedule-item');
        const schedules = [];
        
        scheduleItems.forEach((item, index) => {
            const daySelect = item.querySelector(`select[name="day_of_week_${index}"]`);
            const startTime = item.querySelector(`input[name="start_time_${index}"]`);
            const endTime = item.querySelector(`input[name="end_time_${index}"]`);
            const roomNumber = item.querySelector(`input[name="room_number_${index}"]`);
            
            // If all fields have values
            if (daySelect && startTime && endTime && roomNumber && 
                daySelect.value && startTime.value && endTime.value && roomNumber.value) {
                schedules.push({
                    day_of_week: daySelect.value,
                    start_time: startTime.value,
                    end_time: endTime.value,
                    room_number: roomNumber.value
                });
            }
        });
        
        // Prepare data
        const classData = {
            class_name: className,
            lecturer: lecturer,
            schedules: schedules
        };
        
        // Check if we are creating or updating
        let url = '/api/classes';
        let method = 'POST';
        
        if (classId) {
            url = `/api/classes/${classId}`;
            method = 'PUT';
        }
        
        // Send request with authentication
        const response = await authenticatedFetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(classData)
        });
        
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Hide form and reload classes
        document.getElementById('class-form-container').style.display = 'none';
        loadClassesData();
        
        // Show success message
        alert(`Class ${classId ? 'updated' : 'created'} successfully!`);
        
    } catch (error) {
        console.error('Error saving class:', error);
        alert(`Error: ${error.message}`);
    }
}

// Save student data
async function saveStudent() {
    try {
        // Get form data
        const studentId = document.getElementById('student-id').value;
        const studentName = document.getElementById('student-name').value;
        const fingerprintId = parseInt(document.getElementById('fingerprint-id').value);
        
        // Validate fingerprint ID
        if (isNaN(fingerprintId) || fingerprintId < 1) {
            alert('Please enter a valid fingerprint ID (positive number)');
            return;
        }
        
        // Prepare data
        const studentData = {
            name: studentName,
            fingerprint_id: fingerprintId
        };
        
        // Check if we are creating or updating
        let url = '/api/students';
        let method = 'POST';
        
        if (studentId) {
            url = `/api/students/${studentId}`;
            method = 'PUT';
        }
        
        // Send request with authentication
        const response = await authenticatedFetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(studentData)
        });
        
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Hide form and reload students
        document.getElementById('student-form-container').style.display = 'none';
        loadStudentsData();
        
        // Show success message
        alert(`Student ${studentId ? 'updated' : 'created'} successfully!`);
        
    } catch (error) {
        console.error('Error saving student:', error);
        alert(`Error: ${error.message}`);
    }
}

// Save attendance data (manual recording)
async function saveAttendance() {
    try {
        // Get form data
        const studentId = document.getElementById('attendance-student').value;
        const classId = document.getElementById('attendance-class').value;
        const timestamp = document.getElementById('attendance-timestamp').value;
        
        // Validate fields
        if (!studentId || !classId || !timestamp) {
            alert('Please fill in all fields');
            return;
        }
        
        // Format timestamp to ISO string
        const timestampISO = new Date(timestamp).toISOString();
        
        // Prepare data
        const attendanceData = {
            student_id: studentId,
            class_id: classId,
            timestamp: timestampISO
        };
        
        // Send request with authentication
        const response = await authenticatedFetch('/api/attendance/manual', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(attendanceData)
        });
        
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Show success message
        document.getElementById('attendance-result').style.display = 'block';
        document.getElementById('attendance-message').textContent = 'Attendance recorded successfully!';
        
        // Reset form
        document.getElementById('attendance-form').reset();
        
        // Set current date and time for next record
        const now = new Date();
        const dateTimeString = now.toISOString().slice(0, 16);
        document.getElementById('attendance-timestamp').value = dateTimeString;
        
    } catch (error) {
        console.error('Error recording attendance:', error);
        document.getElementById('attendance-result').style.display = 'block';
        document.getElementById('attendance-message').textContent = `Error: ${error.message}`;
    }
}

// Load dashboard data
async function loadDashboardData() {
    try {
        // Load students count
        const studentsResponse = await authenticatedFetch('/api/students');
        if (studentsResponse.ok) {
            const studentsData = await studentsResponse.json();
            const studentsCount = Object.keys(studentsData.students || {}).length;
            document.getElementById('total-students').textContent = studentsCount;
        }
        
        // Load classes count
        const classesResponse = await authenticatedFetch('/api/classes');
        if (classesResponse.ok) {
            const classesData = await classesResponse.json();
            const classesCount = Object.keys(classesData.classes || {}).length;
            document.getElementById('total-classes').textContent = classesCount;
            
            // Show today's classes
            loadTodaysClasses(classesData.classes || {});
        }
        
        // Load today's attendance count - this would need a new endpoint
        document.getElementById('todays-attendance').textContent = 'N/A';
        
        // Load recent attendance - this would need a new endpoint
        document.getElementById('recent-attendance-data').innerHTML = 
            '<tr><td colspan="3">No recent attendance records</td></tr>';
            
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Load today's classes for the dashboard
function loadTodaysClasses(classes) {
    const todayClasses = document.getElementById('todays-classes');
    
    if (!classes || Object.keys(classes).length === 0) {
        todayClasses.innerHTML = '<p>No classes found</p>';
        return;
    }
    
    // Get current day of week
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const today = days[new Date().getDay()];
    
    // Filter classes that have a schedule for today
    const classesToday = Object.entries(classes).filter(([classId, classData]) => {
        return classData.schedules && classData.schedules.some(schedule => 
            schedule.day_of_week === today);
    });
    
    if (classesToday.length === 0) {
        todayClasses.innerHTML = '<p>No classes scheduled for today</p>';
        return;
    }
    
    // Create HTML for each class
    let html = '';
    classesToday.forEach(([classId, classData]) => {
        const todaySchedules = classData.schedules.filter(schedule => 
            schedule.day_of_week === today);
            
        todaySchedules.forEach(schedule => {
            html += `
                <div class="card">
                    <h3>${classData.class_name}</h3>
                    <p><strong>Lecturer:</strong> ${classData.lecturer}</p>
                    <p><strong>Time:</strong> ${schedule.start_time} - ${schedule.end_time}</p>
                    <p><strong>Room:</strong> ${schedule.room_number}</p>
                </div>
            `;
        });
    });
    
    todayClasses.innerHTML = html;
}

// Load classes data for dropdowns and class list
async function loadClassesData() {
    try {
        const response = await authenticatedFetch('/api/classes');
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        
        const data = await response.json();
        const classes = data.classes || {};
        
        // Update class dropdowns
        updateClassDropdowns(classes);
        
        // Update classes list if we're on the classes page
        const classesList = document.getElementById('classes-list');
        if (classesList) {
            if (Object.keys(classes).length === 0) {
                classesList.innerHTML = '<p>No classes found</p>';
                return;
            }
            
            let html = '';
            Object.entries(classes).forEach(([classId, classData]) => {
                html += `
                    <div class="card">
                        <h3>${classData.class_name}</h3>
                        <p><strong>Lecturer:</strong> ${classData.lecturer}</p>
                        <p><strong>Schedules:</strong></p>
                        <ul>
                            ${classData.schedules.map(schedule => `
                                <li>${schedule.day_of_week}: ${schedule.start_time} - ${schedule.end_time} (Room ${schedule.room_number})</li>
                            `).join('')}
                        </ul>
                        <p><strong>Enrolled Students:</strong> ${(classData.enrolled_students || []).length}</p>
                        <div class="card-actions">
                            <button class="btn secondary edit-class" data-id="${classId}">Edit</button>
                            <button class="btn danger delete-class" data-id="${classId}">Delete</button>
                        </div>
                    </div>
                `;
            });
            
            classesList.innerHTML = html;
            
            // Add event listeners for edit and delete buttons
            document.querySelectorAll('.edit-class').forEach(button => {
                button.addEventListener('click', function() {
                    const classId = this.getAttribute('data-id');
                    const classData = classes[classId];
                    
                    document.getElementById('class-id').value = classId;
                    document.getElementById('class-name').value = classData.class_name;
                    document.getElementById('lecturer').value = classData.lecturer;
                    
                    // Set up schedules
                    const schedulesContainer = document.getElementById('schedules-container');
                    schedulesContainer.innerHTML = '';
                    
                    classData.schedules.forEach((schedule, index) => {
                        addScheduleItem();
                        const scheduleItem = schedulesContainer.children[index];
                        
                        scheduleItem.querySelector(`select[name="day_of_week_${index}"]`).value = schedule.day_of_week;
                        scheduleItem.querySelector(`input[name="start_time_${index}"]`).value = schedule.start_time;
                        scheduleItem.querySelector(`input[name="end_time_${index}"]`).value = schedule.end_time;
                        scheduleItem.querySelector(`input[name="room_number_${index}"]`).value = schedule.room_number;
                    });
                    
                    document.getElementById('class-form-container').style.display = 'block';
                });
            });
            
            document.querySelectorAll('.delete-class').forEach(button => {
                button.addEventListener('click', async function() {
                    if (confirm('Are you sure you want to delete this class?')) {
                        const classId = this.getAttribute('data-id');
                        
                        try {
                            const response = await authenticatedFetch(`/api/classes/${classId}`, {
                                method: 'DELETE'
                            });
                            
                            if (!response.ok) {
                                throw new Error(`Server responded with status: ${response.status}`);
                            }
                            
                            alert('Class deleted successfully!');
                            loadClassesData();
                        } catch (error) {
                            console.error('Error deleting class:', error);
                            alert(`Error: ${error.message}`);
                        }
                    }
                });
            });
        }
    } catch (error) {
        console.error('Error loading classes:', error);
    }
}

// Load students data for dropdowns and student list
async function loadStudentsData() {
    try {
        const response = await authenticatedFetch('/api/students');
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        
        const data = await response.json();
        const students = data.students || {};
        
        // Update student dropdowns
        updateStudentDropdown(students);
        
        // Update students list if we're on the students page
        const studentsList = document.getElementById('students-list');
        if (studentsList) {
            if (Object.keys(students).length === 0) {
                studentsList.innerHTML = '<p>No students found</p>';
                return;
            }
            
            let html = '';
            Object.entries(students).forEach(([studentId, studentData]) => {
                html += `
                    <div class="card">
                        <h3>${studentData.name}</h3>
                        <p><strong>ID:</strong> ${studentId}</p>
                        <p><strong>Fingerprint ID:</strong> ${studentData.fingerprint_id}</p>
                        <p><strong>Enrolled Classes:</strong> ${(studentData.enrolled_classes || []).length}</p>
                        <div class="card-actions">
                            <button class="btn secondary edit-student" data-id="${studentId}">Edit</button>
                            <button class="btn danger delete-student" data-id="${studentId}">Delete</button>
                        </div>
                    </div>
                `;
            });
            
            studentsList.innerHTML = html;
            
            // Add event listeners for edit and delete buttons
            document.querySelectorAll('.edit-student').forEach(button => {
                button.addEventListener('click', function() {
                    const studentId = this.getAttribute('data-id');
                    const studentData = students[studentId];
                    
                    document.getElementById('student-id').value = studentId;
                    document.getElementById('student-name').value = studentData.name;
                    document.getElementById('fingerprint-id').value = studentData.fingerprint_id;
                    
                    document.getElementById('student-form-container').style.display = 'block';
                });
            });
            
            document.querySelectorAll('.delete-student').forEach(button => {
                button.addEventListener('click', async function() {
                    if (confirm('Are you sure you want to delete this student?')) {
                        const studentId = this.getAttribute('data-id');
                        
                        try {
                            const response = await authenticatedFetch(`/api/students/${studentId}`, {
                                method: 'DELETE'
                            });
                            
                            if (!response.ok) {
                                throw new Error(`Server responded with status: ${response.status}`);
                            }
                            
                            alert('Student deleted successfully!');
                            loadStudentsData();
                        } catch (error) {
                            console.error('Error deleting student:', error);
                            alert(`Error: ${error.message}`);
                        }
                    }
                });
            });
        }
    } catch (error) {
        console.error('Error loading students:', error);
    }
}

// Load attendance data for reports
async function loadAttendanceData() {
    // This would fetch attendance data for reports
    // Implementation will depend on the specific endpoint
}

// Generate class attendance report
async function generateClassReport() {
    try {
        const classId = document.getElementById('report-class').value;
        const date = document.getElementById('report-date').value;
        
        if (!classId || !date) {
            alert('Please select a class and date');
            return;
        }
        
        const response = await authenticatedFetch(`/api/attendance/report/${classId}?date=${date}`);
        
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        
        const reportData = await response.json();
        
        // Show report
        document.getElementById('report-title').textContent = 
            `Attendance Report: ${reportData.class_name} (${reportData.date})`;
            
        let html = `
            <div class="report-summary">
                <p><strong>Total Students:</strong> ${reportData.total_students}</p>
                <p><strong>Present:</strong> ${reportData.present_students}</p>
                <p><strong>Absent:</strong> ${reportData.absent_students}</p>
                <p><strong>Attendance Rate:</strong> ${reportData.total_students ? 
                    Math.round((reportData.present_students / reportData.total_students) * 100) : 0}%</p>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Student</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        if (reportData.attendance_list && reportData.attendance_list.length > 0) {
            reportData.attendance_list.forEach(entry => {
                html += `
                    <tr>
                        <td>${entry.name}</td>
                        <td>${entry.status}</td>
                    </tr>
                `;
            });
        } else {
            html += '<tr><td colspan="2">No attendance data for this date</td></tr>';
        }
        
        html += `
                </tbody>
            </table>
        `;
        
        document.getElementById('report-content').innerHTML = html;
        document.getElementById('report-result').style.display = 'block';
        
    } catch (error) {
        console.error('Error generating class report:', error);
        document.getElementById('report-title').textContent = 'Error Generating Report';
        document.getElementById('report-content').innerHTML = `<p class="error-message">${error.message}</p>`;
        document.getElementById('report-result').style.display = 'block';
    }
}

// Generate student attendance summary
async function generateStudentReport() {
    try {
        const studentId = document.getElementById('report-student').value;
        
        if (!studentId) {
            alert('Please select a student');
            return;
        }
        
        const response = await authenticatedFetch(`/api/attendance/student/${studentId}`);
        
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        
        const reportData = await response.json();
        
        // Show report
        document.getElementById('report-title').textContent = 
            `Attendance Summary: ${reportData.student_name}`;
            
        let html = `
            <div class="report-summary">
                <p><strong>Total Classes:</strong> ${reportData.total_classes}</p>
                <p><strong>Classes Attended:</strong> ${reportData.classes_attended}</p>
                <p><strong>Attendance Rate:</strong> ${reportData.total_classes ? 
                    Math.round((reportData.classes_attended / reportData.total_classes) * 100) : 0}%</p>
            </div>
            
            <h3>Attendance by Class</h3>
            <table>
                <thead>
                    <tr>
                        <th>Class</th>
                        <th>Attendance Rate</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        if (reportData.attendance_by_class && Object.keys(reportData.attendance_by_class).length > 0) {
            Object.entries(reportData.attendance_by_class).forEach(([className, data]) => {
                html += `
                    <tr>
                        <td>${className}</td>
                        <td>${data.total_sessions ? 
                            Math.round((data.attended / data.total_sessions) * 100) : 0}%</td>
                    </tr>
                `;
            });
        } else {
            html += '<tr><td colspan="2">No attendance data available</td></tr>';
        }
        
        html += `
                </tbody>
            </table>
        `;
        
        document.getElementById('report-content').innerHTML = html;
        document.getElementById('report-result').style.display = 'block';
        
    } catch (error) {
        console.error('Error generating student report:', error);
        document.getElementById('report-title').textContent = 'Error Generating Report';
        document.getElementById('report-content').innerHTML = `<p class="error-message">${error.message}</p>`;
        document.getElementById('report-result').style.display = 'block';
    }
}

// Update class dropdowns with available classes
function updateClassDropdowns(classes) {
    const attendanceClassSelect = document.getElementById('attendance-class');
    const reportClassSelect = document.getElementById('report-class');
    
    if (attendanceClassSelect) {
        let options = '<option value="">Select Class</option>';
        
        Object.entries(classes).forEach(([classId, classData]) => {
            options += `<option value="${classId}">${classData.class_name}</option>`;
        });
        
        attendanceClassSelect.innerHTML = options;
    }
    
    if (reportClassSelect) {
        let options = '<option value="">Select Class</option>';
        
        Object.entries(classes).forEach(([classId, classData]) => {
            options += `<option value="${classId}">${classData.class_name}</option>`;
        });
        
        reportClassSelect.innerHTML = options;
    }
}

// Update student dropdowns with available students
function updateStudentDropdown(students) {
    const attendanceStudentSelect = document.getElementById('attendance-student');
    const reportStudentSelect = document.getElementById('report-student');
    
    if (attendanceStudentSelect) {
        let options = '<option value="">Select Student</option>';
        
        Object.entries(students).forEach(([studentId, studentData]) => {
            options += `<option value="${studentId}">${studentData.name}</option>`;
        });
        
        attendanceStudentSelect.innerHTML = options;
    }
    
    if (reportStudentSelect) {
        let options = '<option value="">Select Student</option>';
        
        Object.entries(students).forEach(([studentId, studentData]) => {
            options += `<option value="${studentId}">${studentData.name}</option>`;
        });
        
        reportStudentSelect.innerHTML = options;
    }
}