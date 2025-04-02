// Main application script for Fingerprint Attendance System

// Initialize navigation
function initNavigation() {
    // Set up navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links and sections
            navLinks.forEach(l => l.classList.remove('active'));
            document.querySelectorAll('.page-section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Show corresponding section
            const targetPage = this.getAttribute('data-page');
            document.getElementById(targetPage).classList.add('active');
        });
    });
}

// Initialize form handlers
function initFormHandlers() {
    // Class form handler
    const addClassBtn = document.getElementById('add-class-btn');
    if (addClassBtn) {
        addClassBtn.addEventListener('click', function() {
            document.getElementById('class-form-container').style.display = 'block';
            document.getElementById('class-id').value = '';
            document.getElementById('class-name').value = '';
            document.getElementById('lecturer').value = '';
            document.getElementById('schedules-container').innerHTML = '';
            addScheduleField();
        });
    }
    
    // Add schedule button
    const addScheduleBtn = document.getElementById('add-schedule');
    if (addScheduleBtn) {
        addScheduleBtn.addEventListener('click', addScheduleField);
    }
    
    // Cancel class form
    const cancelClassBtn = document.getElementById('cancel-class');
    if (cancelClassBtn) {
        cancelClassBtn.addEventListener('click', function() {
            document.getElementById('class-form-container').style.display = 'none';
        });
    }
    
    // Class form submission
    const classForm = document.getElementById('class-form');
    if (classForm) {
        classForm.addEventListener('submit', handleClassFormSubmit);
    }
    
    // Student form handler
    const addStudentBtn = document.getElementById('add-student-btn');
    if (addStudentBtn) {
        addStudentBtn.addEventListener('click', function() {
            document.getElementById('student-form-container').style.display = 'block';
            document.getElementById('student-id').value = '';
            document.getElementById('student-name').value = '';
            document.getElementById('fingerprint-id').value = '';
        });
    }
    
    // Cancel student form
    const cancelStudentBtn = document.getElementById('cancel-student');
    if (cancelStudentBtn) {
        cancelStudentBtn.addEventListener('click', function() {
            document.getElementById('student-form-container').style.display = 'none';
        });
    }
    
    // Student form submission
    const studentForm = document.getElementById('student-form');
    if (studentForm) {
        studentForm.addEventListener('submit', handleStudentFormSubmit);
    }
    
    // Manual attendance form submission
    const attendanceForm = document.getElementById('attendance-form');
    if (attendanceForm) {
        attendanceForm.addEventListener('submit', handleAttendanceFormSubmit);
    }
    
    // Class report form submission
    const classReportForm = document.getElementById('class-report-form');
    if (classReportForm) {
        classReportForm.addEventListener('submit', handleClassReportFormSubmit);
    }
    
    // Student report form submission
    const studentReportForm = document.getElementById('student-report-form');
    if (studentReportForm) {
        studentReportForm.addEventListener('submit', handleStudentReportFormSubmit);
    }
    
    // Load students and classes for dropdowns
    loadStudentsForDropdown();
    loadClassesForDropdown();
}

// Load dashboard data
function loadDashboardData() {
    console.log("Loading dashboard data...");
    
    // In simulation mode, use fake data
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        simulateDashboardData();
        return;
    }
    
    // Load real data (not implemented yet)
    // This would make authenticated API calls to get real data
}

// Simulate dashboard data for development
function simulateDashboardData() {
    console.log("Using simulated dashboard data");
    
    // Update stats
    document.getElementById('total-students').textContent = '15';
    document.getElementById('total-classes').textContent = '3';
    document.getElementById('todays-attendance').textContent = '7 / 15';
    
    // Display today's classes
    const todaysClasses = document.getElementById('todays-classes');
    todaysClasses.innerHTML = `
        <div class="card">
            <h3>Computer Science 101</h3>
            <p><strong>Time:</strong> 09:00 - 10:30</p>
            <p><strong>Room:</strong> CS-301</p>
            <p><strong>Lecturer:</strong> Dr. Smith</p>
        </div>
        <div class="card">
            <h3>Database Systems</h3>
            <p><strong>Time:</strong> 13:00 - 14:30</p>
            <p><strong>Room:</strong> CS-105</p>
            <p><strong>Lecturer:</strong> Prof. Johnson</p>
        </div>
    `;
    
    // Display recent attendance
    const recentAttendance = document.getElementById('recent-attendance-data');
    recentAttendance.innerHTML = `
        <tr>
            <td>John Doe</td>
            <td>Computer Science 101</td>
            <td>Today, 09:05</td>
        </tr>
        <tr>
            <td>Jane Smith</td>
            <td>Computer Science 101</td>
            <td>Today, 09:08</td>
        </tr>
        <tr>
            <td>Alex Johnson</td>
            <td>Computer Science 101</td>
            <td>Today, 09:12</td>
        </tr>
    `;
}

// Add a schedule field to the class form
function addScheduleField() {
    const container = document.getElementById('schedules-container');
    const scheduleId = Date.now(); // Unique ID
    
    const scheduleHtml = `
        <div class="schedule-item" id="schedule-${scheduleId}">
            <div>
                <label for="day-${scheduleId}">Day:</label>
                <select id="day-${scheduleId}" class="schedule-day" required>
                    <option value="Monday">Monday</option>
                    <option value="Tuesday">Tuesday</option>
                    <option value="Wednesday">Wednesday</option>
                    <option value="Thursday">Thursday</option>
                    <option value="Friday">Friday</option>
                    <option value="Saturday">Saturday</option>
                    <option value="Sunday">Sunday</option>
                </select>
            </div>
            <div>
                <label for="start-${scheduleId}">Start:</label>
                <input type="time" id="start-${scheduleId}" class="schedule-start" required>
            </div>
            <div>
                <label for="end-${scheduleId}">End:</label>
                <input type="time" id="end-${scheduleId}" class="schedule-end" required>
            </div>
            <div>
                <label for="room-${scheduleId}">Room:</label>
                <input type="text" id="room-${scheduleId}" class="schedule-room" required>
            </div>
            <button type="button" class="remove-schedule" onclick="removeSchedule('schedule-${scheduleId}')">×</button>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', scheduleHtml);
}

// Remove a schedule field
function removeSchedule(id) {
    document.getElementById(id).remove();
}

// Handle class form submission
async function handleClassFormSubmit(e) {
    e.preventDefault();
    
    // Get form data
    const classId = document.getElementById('class-id').value;
    const className = document.getElementById('class-name').value;
    const lecturer = document.getElementById('lecturer').value;
    
    // Get schedules
    const schedules = [];
    const scheduleItems = document.querySelectorAll('.schedule-item');
    scheduleItems.forEach(item => {
        const daySelect = item.querySelector('.schedule-day');
        const startTime = item.querySelector('.schedule-start').value;
        const endTime = item.querySelector('.schedule-end').value;
        const roomNumber = item.querySelector('.schedule-room').value;
        
        schedules.push({
            day_of_week: daySelect.value,
            start_time: startTime,
            end_time: endTime,
            room_number: roomNumber
        });
    });
    
    // Create class data object
    const classData = {
        class_name: className,
        lecturer: lecturer,
        schedules: schedules
    };
    
    console.log("Class data:", classData);
    
    try {
        // Determine if this is an edit or a new class
        const isEdit = classId && classId.trim() !== '';
        const url = isEdit ? `/api/classes/${classId}` : '/api/classes';
        const method = isEdit ? 'PUT' : 'POST';
        
        // Send request to API
        const response = await authenticatedFetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(classData)
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        // Hide form and reload classes
        document.getElementById('class-form-container').style.display = 'none';
        loadClasses();
        
        // Show success message
        alert(isEdit ? 'Class updated successfully' : 'Class created successfully');
        
    } catch (error) {
        console.error('Error saving class:', error);
        alert(`Failed to save class: ${error.message}`);
    }
}

// Load classes from API
async function loadClasses() {
    console.log("Loading classes...");
    
    const classesList = document.getElementById('classes-list');
    
    try {
        // API request to get classes
        const response = await authenticatedFetch('/api/classes');
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const classes = await response.json();
        
        // Create HTML for classes
        if (Object.keys(classes).length === 0) {
            classesList.innerHTML = '<p>No classes found. Create a class using the button above.</p>';
            return;
        }
        
        let html = '';
        for (const classId in classes) {
            const classData = classes[classId];
            html += createClassCard(classId, classData);
        }
        
        classesList.innerHTML = html;
        
        // Add event listeners for edit/delete buttons
        document.querySelectorAll('.edit-class-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const classId = this.getAttribute('data-id');
                editClass(classId);
            });
        });
        
        document.querySelectorAll('.delete-class-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const classId = this.getAttribute('data-id');
                deleteClass(classId);
            });
        });
        
    } catch (error) {
        console.error('Error loading classes:', error);
        classesList.innerHTML = `<p>Error loading classes: ${error.message}</p>`;
    }
}

// Simulation mode - placeholder functions
function loadStudentsForDropdown() {
    console.log("Loading students for dropdown...");
    // In a real app, this would make an API call
    // For now, we'll just populate with dummy data
    
    const studentSelects = document.querySelectorAll('#attendance-student, #report-student, #student-id');
    studentSelects.forEach(select => {
        select.innerHTML = `
            <option value="">Select Student</option>
            <option value="1">John Doe</option>
            <option value="2">Jane Smith</option>
            <option value="3">Alex Johnson</option>
        `;
    });
    
    // Also populate fingerprint ID selector
    const fingerprintSelect = document.getElementById('fingerprint-id');
    if (fingerprintSelect) {
        fingerprintSelect.innerHTML = `
            <option value="">Select Fingerprint ID</option>
            <option value="1">1 - John Doe</option>
            <option value="2">2 - Jane Smith</option>
            <option value="3">3 - Alex Johnson</option>
        `;
    }
}

function loadClassesForDropdown() {
    console.log("Loading classes for dropdown...");
    // In a real app, this would make an API call
    // For now, we'll just populate with dummy data
    
    const classSelects = document.querySelectorAll('#attendance-class, #report-class');
    classSelects.forEach(select => {
        select.innerHTML = `
            <option value="">Select Class</option>
            <option value="1">Computer Science 101</option>
            <option value="2">Database Systems</option>
            <option value="3">Machine Learning</option>
        `;
    });
}

// Create class card HTML
function createClassCard(classId, classData) {
    // Format schedules
    const schedulesList = classData.schedules.map(schedule => {
        return `
            <div class="schedule">
                <span>${schedule.day_of_week}</span>
                <span>${schedule.start_time} - ${schedule.end_time}</span>
                <span>Room: ${schedule.room_number}</span>
            </div>
        `;
    }).join('');
    
    return `
        <div class="card" data-id="${classId}">
            <h3>${classData.class_name}</h3>
            <p><strong>Lecturer:</strong> ${classData.lecturer}</p>
            <div class="schedules">
                <h4>Schedules:</h4>
                ${schedulesList}
            </div>
            <div class="card-actions">
                <button class="btn edit-class-btn" data-id="${classId}">Edit</button>
                <button class="btn danger delete-class-btn" data-id="${classId}">Delete</button>
            </div>
        </div>
    `;
}

// For demo purposes only
function handleStudentFormSubmit(e) {
    e.preventDefault();
    alert("Student form submission would be processed here (simulation mode)");
    document.getElementById('student-form-container').style.display = 'none';
}

function handleAttendanceFormSubmit(e) {
    e.preventDefault();
    document.getElementById('attendance-result').style.display = 'block';
    document.getElementById('attendance-message').textContent = 'Attendance recorded successfully (simulation mode)';
    setTimeout(() => {
        document.getElementById('attendance-result').style.display = 'none';
        document.getElementById('attendance-form').reset();
    }, 3000);
}

function handleClassReportFormSubmit(e) {
    e.preventDefault();
    
    const className = document.querySelector('#report-class option:checked').text;
    const date = document.getElementById('report-date').value;
    
    document.getElementById('report-title').textContent = `Attendance Report: ${className} (${date})`;
    
    document.getElementById('report-content').innerHTML = `
        <div class="report-summary">
            <p><strong>Total Students:</strong> 15</p>
            <p><strong>Present:</strong> 12</p>
            <p><strong>Absent:</strong> 3</p>
            <p><strong>Attendance Rate:</strong> 80%</p>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Student Name</th>
                    <th>Status</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>John Doe</td>
                    <td>Present</td>
                    <td>09:05</td>
                </tr>
                <tr>
                    <td>Jane Smith</td>
                    <td>Present</td>
                    <td>09:08</td>
                </tr>
                <tr>
                    <td>Alex Johnson</td>
                    <td>Present</td>
                    <td>09:12</td>
                </tr>
                <tr>
                    <td>Sarah Williams</td>
                    <td>Absent</td>
                    <td>-</td>
                </tr>
            </tbody>
        </table>
    `;
    
    document.getElementById('report-result').style.display = 'block';
}

function handleStudentReportFormSubmit(e) {
    e.preventDefault();
    
    const studentName = document.querySelector('#report-student option:checked').text;
    
    document.getElementById('report-title').textContent = `Attendance Summary: ${studentName}`;
    
    document.getElementById('report-content').innerHTML = `
        <div class="report-summary">
            <p><strong>Total Classes:</strong> 3</p>
            <p><strong>Attendance Rate:</strong> 85%</p>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Class Name</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Computer Science 101</td>
                    <td>2023-06-01</td>
                    <td>Present</td>
                    <td>09:05</td>
                </tr>
                <tr>
                    <td>Computer Science 101</td>
                    <td>2023-06-03</td>
                    <td>Present</td>
                    <td>09:08</td>
                </tr>
                <tr>
                    <td>Database Systems</td>
                    <td>2023-06-02</td>
                    <td>Present</td>
                    <td>13:02</td>
                </tr>
                <tr>
                    <td>Machine Learning</td>
                    <td>2023-06-04</td>
                    <td>Absent</td>
                    <td>-</td>
                </tr>
            </tbody>
        </table>
    `;
    
    document.getElementById('report-result').style.display = 'block';
}