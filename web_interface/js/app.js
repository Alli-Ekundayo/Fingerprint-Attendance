// Fingerprint Attendance System - Frontend JavaScript

// API Base URL - adjust this as needed
const API_BASE_URL = '/api';

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize page navigation
    initNavigation();
    
    // Initialize form handlers
    initFormHandlers();
    
    // Load initial data
    loadDashboardData();
    loadClassesData();
    loadStudentsData();
    
    // Add event listeners for report generation
    document.getElementById('generate-report-btn').addEventListener('click', generateClassReport);
    document.getElementById('generate-student-report-btn').addEventListener('click', generateStudentReport);
    
    // Add event listener for attendance filter
    document.getElementById('attendance-filter-btn').addEventListener('click', loadAttendanceData);
    
    // Set today's date as default for date inputs
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('attendance-date').value = today;
    document.getElementById('report-date').value = today;
    
    // Initialize datetime-local with current time
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('attendance-time').value = now.toISOString().slice(0, 16);
});

// Page navigation
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links and pages
            navLinks.forEach(l => l.classList.remove('active'));
            document.querySelectorAll('.page-content').forEach(page => page.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Show the corresponding page
            const pageName = this.getAttribute('data-page');
            document.getElementById(`${pageName}-page`).classList.add('active');
        });
    });
}

// Initialize form handlers
function initFormHandlers() {
    // Add Schedule Button
    document.getElementById('add-schedule-btn').addEventListener('click', addScheduleItem);
    
    // Save Class Button
    document.getElementById('save-class-btn').addEventListener('click', saveClass);
    
    // Save Student Button
    document.getElementById('save-student-btn').addEventListener('click', saveStudent);
    
    // Save Attendance Button
    document.getElementById('save-attendance-btn').addEventListener('click', saveAttendance);
}

// Add a new schedule item to the class form
function addScheduleItem() {
    const container = document.getElementById('schedule-container');
    const scheduleItems = container.querySelectorAll('.schedule-item');
    
    // Clone the first schedule item
    const newItem = scheduleItems[0].cloneNode(true);
    
    // Clear the input values
    newItem.querySelectorAll('input, select').forEach(input => {
        input.value = '';
    });
    
    // Add remove button if it's not the first item
    if (!newItem.querySelector('.remove-schedule-btn')) {
        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn btn-sm btn-outline-danger remove-schedule-btn';
        removeBtn.innerHTML = '<i class="bi bi-trash"></i>';
        removeBtn.addEventListener('click', function() {
            this.closest('.schedule-item').remove();
        });
        
        newItem.appendChild(removeBtn);
    }
    
    // Append the new item to the container
    container.appendChild(newItem);
}

// Save a new class
async function saveClass() {
    try {
        const className = document.getElementById('class-name').value;
        const lecturer = document.getElementById('lecturer').value;
        
        // Validate required fields
        if (!className || !lecturer) {
            alert('Please fill in all required fields');
            return;
        }
        
        // Get schedules
        const scheduleItems = document.querySelectorAll('.schedule-item');
        const schedules = [];
        
        for (const item of scheduleItems) {
            const dayOfWeek = item.querySelector('.day-of-week').value;
            const startTime = item.querySelector('.start-time').value;
            const endTime = item.querySelector('.end-time').value;
            const roomNumber = item.querySelector('.room-number').value;
            
            if (!dayOfWeek || !startTime || !endTime || !roomNumber) {
                alert('Please fill in all schedule fields');
                return;
            }
            
            schedules.push({
                day_of_week: dayOfWeek,
                start_time: startTime,
                end_time: endTime,
                room_number: roomNumber
            });
        }
        
        // Create class data
        const classData = {
            class_name: className,
            lecturer: lecturer,
            schedules: schedules
        };
        
        // Send API request
        const response = await fetch(`${API_BASE_URL}/classes/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(classData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Class created successfully');
            
            // Close modal and reset form
            bootstrap.Modal.getInstance(document.getElementById('addClassModal')).hide();
            document.getElementById('add-class-form').reset();
            document.getElementById('schedule-container').innerHTML = document.getElementById('schedule-container').innerHTML;
            
            // Reload classes data
            loadClassesData();
            loadDashboardData();
        } else {
            alert(`Error: ${result.detail || 'Failed to create class'}`);
        }
    } catch (error) {
        console.error('Error creating class:', error);
        alert('An error occurred while creating the class');
    }
}

// Save a new student
async function saveStudent() {
    try {
        const studentName = document.getElementById('student-name').value;
        const fingerprintId = parseInt(document.getElementById('fingerprint-id').value);
        
        // Validate required fields
        if (!studentName || isNaN(fingerprintId)) {
            alert('Please fill in all required fields');
            return;
        }
        
        // Create student data
        const studentData = {
            name: studentName,
            fingerprint_id: fingerprintId
        };
        
        // Send API request
        const response = await fetch(`${API_BASE_URL}/students/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(studentData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            const studentId = result.student_id;
            
            // Enroll student in selected classes
            const selectedClasses = [];
            document.querySelectorAll('input[name="class-enrollment"]:checked').forEach(checkbox => {
                selectedClasses.push(checkbox.value);
            });
            
            // Enroll in each class
            for (const classId of selectedClasses) {
                await fetch(`${API_BASE_URL}/classes/${classId}/enroll/${studentId}`, {
                    method: 'POST'
                });
            }
            
            alert('Student created successfully');
            
            // Close modal and reset form
            bootstrap.Modal.getInstance(document.getElementById('addStudentModal')).hide();
            document.getElementById('add-student-form').reset();
            
            // Reload students data
            loadStudentsData();
            loadDashboardData();
        } else {
            alert(`Error: ${result.detail || 'Failed to create student'}`);
        }
    } catch (error) {
        console.error('Error creating student:', error);
        alert('An error occurred while creating the student');
    }
}

// Save attendance record
async function saveAttendance() {
    try {
        const studentId = document.getElementById('attendance-student').value;
        const classId = document.getElementById('attendance-class-input').value;
        const timestamp = document.getElementById('attendance-time').value.replace('T', ' ');
        
        // Validate required fields
        if (!studentId || !classId || !timestamp) {
            alert('Please fill in all required fields');
            return;
        }
        
        // Create attendance data
        const attendanceData = {
            student_id: studentId,
            class_id: classId,
            timestamp: timestamp
        };
        
        // Send API request
        const response = await fetch(`${API_BASE_URL}/attendance/manual`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(attendanceData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Attendance recorded successfully');
            
            // Close modal and reset form
            bootstrap.Modal.getInstance(document.getElementById('recordAttendanceModal')).hide();
            document.getElementById('record-attendance-form').reset();
            
            // Reload attendance data
            loadAttendanceData();
            loadDashboardData();
        } else {
            alert(`Error: ${result.detail || 'Failed to record attendance'}`);
        }
    } catch (error) {
        console.error('Error recording attendance:', error);
        alert('An error occurred while recording attendance');
    }
}

// Load dashboard data
async function loadDashboardData() {
    try {
        // Get counts for dashboard
        const [studentsResponse, classesResponse] = await Promise.all([
            fetch(`${API_BASE_URL}/students/`),
            fetch(`${API_BASE_URL}/classes/`)
        ]);
        
        const studentsData = await studentsResponse.json();
        const classesData = await classesResponse.json();
        
        // Update dashboard stats
        const students = studentsData.students || {};
        const classes = classesData.classes || {};
        
        document.getElementById('total-students').textContent = Object.keys(students).length;
        document.getElementById('total-classes').textContent = Object.keys(classes).length;
        
        // Load today's classes
        loadTodaysClasses(classes);
        
        // TODO: Load today's attendance count and recent attendance
        // This would typically come from a specific API endpoint
        document.getElementById('todays-attendance').textContent = '0';
        document.getElementById('recent-attendance-table').innerHTML = '<tr><td colspan="3" class="text-center">No recent attendance</td></tr>';
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Load today's classes for the dashboard
function loadTodaysClasses(classes) {
    if (!classes || Object.keys(classes).length === 0) {
        return;
    }
    
    // Get current day of week
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const currentDay = days[new Date().getDay()];
    
    // Filter classes for today
    const todaysClasses = [];
    
    for (const classId in classes) {
        const classInfo = classes[classId];
        const schedules = classInfo.schedules || [];
        
        for (const schedule of schedules) {
            if (schedule.day_of_week === currentDay) {
                todaysClasses.push({
                    class_name: classInfo.class_name,
                    lecturer: classInfo.lecturer,
                    start_time: schedule.start_time,
                    end_time: schedule.end_time,
                    room_number: schedule.room_number
                });
            }
        }
    }
    
    // Sort by start time
    todaysClasses.sort((a, b) => a.start_time.localeCompare(b.start_time));
    
    // Update the table
    const tableBody = document.getElementById('todays-classes-table');
    
    if (todaysClasses.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="4" class="text-center">No classes scheduled for today</td></tr>';
        return;
    }
    
    tableBody.innerHTML = '';
    
    for (const cls of todaysClasses) {
        tableBody.innerHTML += `
            <tr>
                <td>${cls.class_name}</td>
                <td>${cls.lecturer}</td>
                <td>${cls.start_time} - ${cls.end_time}</td>
                <td>${cls.room_number}</td>
            </tr>
        `;
    }
}

// Load classes data
async function loadClassesData() {
    try {
        const response = await fetch(`${API_BASE_URL}/classes/`);
        const data = await response.json();
        
        const classes = data.classes || {};
        
        // Update classes table
        const tableBody = document.getElementById('classes-table');
        
        if (Object.keys(classes).length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No classes found</td></tr>';
            return;
        }
        
        tableBody.innerHTML = '';
        
        for (const classId in classes) {
            const classInfo = classes[classId];
            const schedules = classInfo.schedules || [];
            
            // Format schedules
            const scheduleText = schedules.map(s => 
                `${s.day_of_week} ${s.start_time}-${s.end_time} (${s.room_number})`
            ).join('<br>');
            
            // Count enrolled students
            const enrolledCount = (classInfo.enrolled_students || []).length;
            
            tableBody.innerHTML += `
                <tr>
                    <td>${classInfo.class_name}</td>
                    <td>${classInfo.lecturer}</td>
                    <td>${scheduleText}</td>
                    <td>${enrolledCount} students</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary action-btn">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger action-btn">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }
        
        // Update class dropdowns
        updateClassDropdowns(classes);
        
    } catch (error) {
        console.error('Error loading classes:', error);
    }
}

// Load students data
async function loadStudentsData() {
    try {
        const response = await fetch(`${API_BASE_URL}/students/`);
        const data = await response.json();
        
        const students = data.students || {};
        
        // Update students table
        const tableBody = document.getElementById('students-table');
        
        if (Object.keys(students).length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" class="text-center">No students found</td></tr>';
            return;
        }
        
        // Load class data for mapping class IDs to names
        const classesResponse = await fetch(`${API_BASE_URL}/classes/`);
        const classesData = await classesResponse.json();
        const classes = classesData.classes || {};
        
        tableBody.innerHTML = '';
        
        for (const studentId in students) {
            const student = students[studentId];
            const enrolledClasses = student.enrolled_classes || [];
            
            // Map class IDs to class names
            const classNames = enrolledClasses.map(classId => {
                return classes[classId] ? classes[classId].class_name : 'Unknown Class';
            }).join(', ');
            
            tableBody.innerHTML += `
                <tr>
                    <td>${student.name}</td>
                    <td>${student.fingerprint_id}</td>
                    <td>${classNames}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary action-btn">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger action-btn">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }
        
        // Update student dropdown
        updateStudentDropdown(students);
        
    } catch (error) {
        console.error('Error loading students:', error);
    }
}

// Load attendance data
async function loadAttendanceData() {
    // Note: This would typically filter based on selected date and class
    // but our API doesn't have this functionality yet, so this is a placeholder
    
    // For now, we'll leave it as a placeholder
    document.getElementById('attendance-table').innerHTML = 
        '<tr><td colspan="4" class="text-center">No attendance records found</td></tr>';
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
        
        // Request report data
        const response = await fetch(`${API_BASE_URL}/attendance/report/${classId}?date=${date}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate report');
        }
        
        const reportData = await response.json();
        
        // Display report
        const resultsContainer = document.getElementById('report-results');
        
        resultsContainer.innerHTML = `
            <div class="row mb-4">
                <div class="col-12">
                    <h4>${reportData.class_name} - Attendance Report</h4>
                    <p>Date: ${reportData.date}</p>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="report-stat-card">
                        <div class="report-stat-value">${reportData.total_students}</div>
                        <div class="report-stat-label">Total Students</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="report-stat-card">
                        <div class="report-stat-value">${reportData.present_students}</div>
                        <div class="report-stat-label">Present</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="report-stat-card">
                        <div class="report-stat-value">${reportData.absent_students}</div>
                        <div class="report-stat-label">Absent</div>
                    </div>
                </div>
            </div>
            
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Student Name</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${reportData.attendance_list.map(item => `
                            <tr>
                                <td>${item.name}</td>
                                <td>
                                    <span class="badge ${item.status === 'present' ? 'bg-success' : 'bg-danger'}">
                                        ${item.status}
                                    </span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
    } catch (error) {
        console.error('Error generating report:', error);
        alert(`Error: ${error.message}`);
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
        
        // Request student attendance data
        const response = await fetch(`${API_BASE_URL}/attendance/student/${studentId}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate summary');
        }
        
        const summaryData = await response.json();
        
        // Display summary
        const resultsContainer = document.getElementById('report-results');
        
        resultsContainer.innerHTML = `
            <div class="row mb-4">
                <div class="col-12">
                    <h4>${summaryData.name} - Attendance Summary</h4>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-12">
                    <p>Enrolled in ${summaryData.enrolled_classes} classes</p>
                </div>
            </div>
            
            ${summaryData.class_attendance.length === 0 ? 
                '<p>No attendance records found for this student.</p>' :
                `<div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Class</th>
                                <th>Total Days</th>
                                <th>Days Attended</th>
                                <th>Attendance Rate</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${summaryData.class_attendance.map(item => `
                                <tr>
                                    <td>${item.class_name}</td>
                                    <td>${item.total_days}</td>
                                    <td>${item.attended_days}</td>
                                    <td>
                                        <div class="progress">
                                            <div class="progress-bar" role="progressbar" 
                                                style="width: ${item.attendance_percentage}%;" 
                                                aria-valuenow="${item.attendance_percentage}" 
                                                aria-valuemin="0" aria-valuemax="100">
                                                ${item.attendance_percentage}%
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>`
            }
        `;
        
    } catch (error) {
        console.error('Error generating student summary:', error);
        alert(`Error: ${error.message}`);
    }
}

// Update class dropdown options
function updateClassDropdowns(classes) {
    // Add classes to the dropdowns
    const classDropdowns = [
        document.getElementById('attendance-class'),
        document.getElementById('report-class'),
        document.getElementById('attendance-class-input')
    ];
    
    // For each dropdown
    classDropdowns.forEach(dropdown => {
        if (!dropdown) return;
        
        // Keep the default option
        const defaultOption = dropdown.querySelector('option');
        dropdown.innerHTML = '';
        if (defaultOption) {
            dropdown.appendChild(defaultOption);
        }
        
        // Add each class as an option
        for (const classId in classes) {
            const option = document.createElement('option');
            option.value = classId;
            option.textContent = classes[classId].class_name;
            dropdown.appendChild(option);
        }
    });
    
    // Update class enrollment checkboxes in student form
    const enrollmentContainer = document.getElementById('class-enrollment-checkboxes');
    
    if (Object.keys(classes).length === 0) {
        enrollmentContainer.innerHTML = `
            <div class="form-check">
                <input class="form-check-input" type="checkbox" disabled>
                <label class="form-check-label">No classes available</label>
            </div>
        `;
        return;
    }
    
    enrollmentContainer.innerHTML = '';
    
    for (const classId in classes) {
        enrollmentContainer.innerHTML += `
            <div class="form-check">
                <input class="form-check-input" type="checkbox" value="${classId}" name="class-enrollment" id="class-${classId}">
                <label class="form-check-label" for="class-${classId}">${classes[classId].class_name}</label>
            </div>
        `;
    }
}

// Update student dropdown
function updateStudentDropdown(students) {
    const studentDropdowns = [
        document.getElementById('attendance-student'),
        document.getElementById('report-student')
    ];
    
    studentDropdowns.forEach(dropdown => {
        if (!dropdown) return;
        
        // Keep the default option
        const defaultOption = dropdown.querySelector('option');
        dropdown.innerHTML = '';
        if (defaultOption) {
            dropdown.appendChild(defaultOption);
        }
        
        // Add each student as an option
        for (const studentId in students) {
            const option = document.createElement('option');
            option.value = studentId;
            option.textContent = students[studentId].name;
            dropdown.appendChild(option);
        }
    });
}