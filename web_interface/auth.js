// Firebase Authentication for Fingerprint Attendance System

// Initialize Firebase Auth
function initializeAuth() {
    // Check if the user is already signed in
    firebase.auth().onAuthStateChanged(function(user) {
        if (user) {
            // User is signed in
            console.log("User is signed in:", user.email);
            document.getElementById('auth-status').textContent = `Logged in as: ${user.email}`;
            document.getElementById('login-container').style.display = 'none';
            document.getElementById('app-container').style.display = 'block';
            document.getElementById('logout-button').style.display = 'block';
            
            // Load initial data
            loadDashboardData();
        } else {
            // User is signed out
            console.log("User is signed out");
            document.getElementById('auth-status').textContent = 'Not logged in';
            document.getElementById('login-container').style.display = 'block';
            document.getElementById('app-container').style.display = 'none';
            document.getElementById('logout-button').style.display = 'none';
        }
    });

    // Set up login form
    document.getElementById('login-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        // Sign in with email and password
        firebase.auth().signInWithEmailAndPassword(email, password)
            .then((userCredential) => {
                // Signed in successfully
                const user = userCredential.user;
                console.log("Logged in successfully:", user.email);
            })
            .catch((error) => {
                // Handle errors
                const errorCode = error.code;
                const errorMessage = error.message;
                console.error("Login error:", errorCode, errorMessage);
                
                // Show error message to user
                document.getElementById('login-error').textContent = getAuthErrorMessage(errorCode);
                document.getElementById('login-error').style.display = 'block';
            });
    });

    // Set up logout button
    document.getElementById('logout-button').addEventListener('click', function() {
        firebase.auth().signOut().then(() => {
            console.log("User signed out successfully");
        }).catch((error) => {
            console.error("Error signing out:", error);
        });
    });
}

// Get user-friendly error messages
function getAuthErrorMessage(errorCode) {
    switch(errorCode) {
        case 'auth/invalid-email':
            return 'Invalid email format.';
        case 'auth/user-disabled':
            return 'This account has been disabled.';
        case 'auth/user-not-found':
            return 'No account found with this email.';
        case 'auth/wrong-password':
            return 'Incorrect password.';
        case 'auth/too-many-requests':
            return 'Too many login attempts. Please try again later.';
        default:
            return 'Authentication error. Please try again.';
    }
}

// Check if user is authenticated before API calls
function checkAuth() {
    const user = firebase.auth().currentUser;
    if (!user) {
        console.error("User not authenticated");
        window.location.href = '/';
        return false;
    }
    return true;
}

// Add authentication headers to fetch requests
async function authenticatedFetch(url, options = {}) {
    const user = firebase.auth().currentUser;
    if (!user) {
        throw new Error("User not authenticated");
    }
    
    // Get the ID token
    const token = await user.getIdToken();
    
    // Add token to headers
    const headers = {
        ...(options.headers || {}),
        'Authorization': `Bearer ${token}`
    };
    
    // Return the fetch with auth headers
    return fetch(url, {
        ...options,
        headers
    });
}