// Fingerprint Management JavaScript
// This file handles the fingerprint enrollment and removal interface

/**
 * Initialize the fingerprint management interface
 */
function initFingerprintManagement(idToken) {
    console.log("Initializing fingerprint management interface...");
    
    // Update fingerprint sensor status
    updateFingerprintStatus(idToken);
    
    // Load students for the dropdown
    loadStudentsForDropdown(idToken);
    
    // Handle fingerprint enrollment form submission
    const enrollForm = document.getElementById('fingerprint-enroll-form');
    if (enrollForm) {
        enrollForm.addEventListener('submit', handleEnrollSubmit);
    }
    
    // Handle fingerprint removal form submission
    const removeForm = document.getElementById('fingerprint-remove-form');
    if (removeForm) {
        removeForm.addEventListener('submit', handleRemoveSubmit);
    }
}

/**
 * Update the fingerprint sensor status display
 */
async function updateFingerprintStatus(idToken) {
    const statusContainer = document.querySelector('.sensor-status');
    
    try {
        // In simulation mode, use fake data
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            // Simulate sensor status for development
            statusContainer.innerHTML = `
                <h3>Fingerprint Sensor Status</h3>
                <p>Status: <span class="status-text">Connected</span></p>
                <p>Sensor Type: R30X Optical Sensor (Simulation Mode)</p>
                <p>Templates Stored: 3</p>
            `;
            statusContainer.classList.add('status-connected');
            return;
        }
        
        // Make API request to check sensor status
        const response = await fetch('/api/fingerprints/status', {
            headers: {
                'Authorization': `Bearer ${idToken}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const statusData = await response.json();
        
        // Update the status container
        let statusHtml = `<h3>Fingerprint Sensor Status</h3>`;
        
        if (statusData.status === 'connected') {
            statusHtml += `
                <p>Status: <span class="status-text">Connected</span></p>
                <p>Sensor Type: ${statusData.data.sensor_type}</p>
                <p>Templates Stored: ${statusData.data.template_count}</p>
            `;
            statusContainer.classList.add('status-connected');
        } else if (statusData.status === 'disconnected') {
            statusHtml += `
                <p>Status: <span class="status-text">Disconnected</span></p>
                <p>The fingerprint sensor is not connected or not responding.</p>
                <p>Please check the hardware connection and restart the system.</p>
            `;
            statusContainer.classList.add('status-disconnected');
        } else {
            statusHtml += `
                <p>Status: <span class="status-text">Error</span></p>
                <p>Error message: ${statusData.message}</p>
            `;
            statusContainer.classList.add('status-error');
        }
        
        statusContainer.innerHTML = statusHtml;
        
    } catch (error) {
        console.error('Error checking fingerprint sensor status:', error);
        
        statusContainer.innerHTML = `
            <h3>Fingerprint Sensor Status</h3>
            <p>Status: <span class="status-text">Error</span></p>
            <p>Failed to check sensor status: ${error.message}</p>
        `;
        statusContainer.classList.add('status-error');
    }
}

/**
 * Load students for the dropdown selection
 */
async function loadStudentsForDropdown(idToken) {
    const studentSelect = document.getElementById('student-id');
    const fingerprintSelect = document.getElementById('fingerprint-id');
    
    if (!studentSelect || !fingerprintSelect) return;
    
    try {
        // In simulation mode, use fake data
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            // Already populated in app.js
            return;
        }
        
        // Make API request to get students
        const response = await fetch('/api/students', {
            headers: {
                'Authorization': `Bearer ${idToken}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const students = await response.json();
        
        // Populate student dropdown
        let studentOptions = '<option value="">Select Student</option>';
        let fingerprintOptions = '<option value="">Select Fingerprint ID</option>';
        
        for (const studentId in students) {
            const student = students[studentId];
            studentOptions += `<option value="${studentId}">${student.name}</option>`;
            
            if (student.fingerprint_id > 0) {
                fingerprintOptions += `<option value="${student.fingerprint_id}">${student.fingerprint_id} - ${student.name}</option>`;
            }
        }
        
        studentSelect.innerHTML = studentOptions;
        fingerprintSelect.innerHTML = fingerprintOptions;
        
    } catch (error) {
        console.error('Error loading students for dropdown:', error);
        
        // Show error message
        studentSelect.innerHTML = '<option value="">Error loading students</option>';
        fingerprintSelect.innerHTML = '<option value="">Error loading fingerprints</option>';
    }
}

/**
 * Handle enrollment form submission
 */
async function handleEnrollSubmit(event) {
    event.preventDefault();
    
    const studentId = document.getElementById('student-id').value;
    if (!studentId) {
        alert('Please select a student');
        return;
    }
    
    const enrollmentStatus = document.getElementById('enrollment-status');
    enrollmentStatus.innerHTML = '<div class="alert alert-info">Initiating fingerprint enrollment... Please place finger on the sensor.</div>';
    
    try {
        // In simulation mode, simulate enrollment
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            // Simulate fingerprint enrollment
            await simulateEnrollment(enrollmentStatus);
            return;
        }
        
        // Make API request to enroll fingerprint
        const response = await authenticatedFetch('/api/fingerprints/enroll', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                student_id: studentId
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `API error: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.status === 'pending') {
            // Enrollment initiated successfully
            enrollmentStatus.innerHTML = `
                <div class="alert alert-info">
                    <p>${result.message}</p>
                    <p>Student: ${result.data.student_name}</p>
                    <p>Fingerprint ID: ${result.data.fingerprint_id}</p>
                </div>
            `;
            
            // Poll for enrollment completion (in a real app)
            // For simulation, we just update after a delay
            setTimeout(() => {
                enrollmentStatus.innerHTML = `
                    <div class="alert alert-success">
                        <p>Fingerprint enrolled successfully!</p>
                        <p>Student: ${result.data.student_name}</p>
                        <p>Fingerprint ID: ${result.data.fingerprint_id}</p>
                    </div>
                `;
                
                // Reload dropdowns after enrollment
                loadStudentsForDropdown(getAuthToken());
                updateFingerprintStatus(getAuthToken());
                
            }, 5000);
        } else {
            // Something unexpected happened
            enrollmentStatus.innerHTML = `
                <div class="alert alert-danger">
                    <p>Unexpected response: ${result.message}</p>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Error enrolling fingerprint:', error);
        
        enrollmentStatus.innerHTML = `
            <div class="alert alert-danger">
                <p>Failed to enroll fingerprint: ${error.message}</p>
            </div>
        `;
    }
}

/**
 * Handle remove form submission
 */
async function handleRemoveSubmit(event) {
    event.preventDefault();
    
    const fingerprintId = document.getElementById('fingerprint-id').value;
    if (!fingerprintId) {
        alert('Please select a fingerprint ID');
        return;
    }
    
    // Confirm deletion
    if (!confirm(`Are you sure you want to remove fingerprint ID ${fingerprintId}?`)) {
        return;
    }
    
    try {
        // In simulation mode, simulate removal
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            // Simulate fingerprint removal
            alert(`Fingerprint ID ${fingerprintId} removed successfully (simulation mode)`);
            return;
        }
        
        // Make API request to remove fingerprint
        const response = await authenticatedFetch('/api/fingerprints/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fingerprint_id: parseInt(fingerprintId)
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `API error: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Show success message
        alert(`${result.message}`);
        
        // Reload dropdowns after removal
        loadStudentsForDropdown(getAuthToken());
        updateFingerprintStatus(getAuthToken());
        
    } catch (error) {
        console.error('Error removing fingerprint:', error);
        alert(`Failed to remove fingerprint: ${error.message}`);
    }
}

/**
 * Simulate fingerprint enrollment (for development only)
 */
async function simulateEnrollment(statusElement) {
    // Simulate the enrollment process with delays
    
    // Step 1: Starting
    statusElement.innerHTML = `
        <div class="alert alert-info">
            <p>Starting enrollment process...</p>
            <p>Place your finger on the sensor.</p>
        </div>
    `;
    
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Step 2: First scan
    statusElement.innerHTML = `
        <div class="alert alert-info">
            <p>First scan complete.</p>
            <p>Remove finger from the sensor.</p>
        </div>
    `;
    
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Step 3: Second scan
    statusElement.innerHTML = `
        <div class="alert alert-info">
            <p>Place the same finger on the sensor again.</p>
        </div>
    `;
    
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Step 4: Complete
    statusElement.innerHTML = `
        <div class="alert alert-success">
            <p>Fingerprint enrolled successfully! (Simulation Mode)</p>
            <p>Student: John Doe</p>
            <p>Fingerprint ID: 4</p>
        </div>
    `;
    
    // Update dropdowns (though they're static in simulation mode)
}

/**
 * Helper function to get auth token
 */
function getAuthToken() {
    // In development/simulation mode, return demo token
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'demo-token-for-development';
    }
    
    // In production, get token from Firebase Auth
    const user = firebase.auth().currentUser;
    if (!user) {
        throw new Error('User not authenticated');
    }
    
    return user.getIdToken();
}