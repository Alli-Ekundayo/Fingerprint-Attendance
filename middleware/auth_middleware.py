"""
Authentication middleware for the Fingerprint Attendance System API

This module provides FastAPI middleware and dependencies for protecting
API routes with Firebase Authentication.
"""

import os
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    try:
        # Get configuration from environment variables
        cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase_config/credentials.json')
        project_id = os.environ.get('FIREBASE_PROJECT_ID', 'fingerprint-attendance-system')
        simulation_mode = os.environ.get('FIREBASE_SIMULATION', 'false').lower() == 'true'
        
        logger.info(f"Initializing Firebase with Project ID: {project_id}, Simulation mode: {simulation_mode}")
        
        if simulation_mode:
            # Initialize without credentials in simulation mode
            firebase_admin.initialize_app(options={
                'projectId': project_id
            })
            logger.info(f"Firebase Admin SDK initialized in simulation mode with project ID: {project_id}")
        elif os.path.exists(cred_path):
            # Initialize with credentials file
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'projectId': project_id
            })
            logger.info(f"Firebase Admin SDK initialized with credentials from {cred_path}")
        else:
            # Initialize without credentials for demo/development purposes
            firebase_admin.initialize_app(options={
                'projectId': project_id
            })
            logger.info(f"Firebase Admin SDK initialized with default project ID: {project_id}")
    except Exception as e:
        logger.error(f"Error initializing Firebase Admin SDK: {str(e)}")
        # Don't fail completely, just log the error
        if not firebase_admin._apps:
            firebase_admin.initialize_app(options={
                'projectId': 'fingerprint-attendance-system'
            })
            logger.warning("Firebase Admin SDK initialized with fallback configuration")

# HTTP Bearer token setup for FastAPI
security = HTTPBearer()

def is_simulation_mode():
    """Check if the application is running in simulation mode"""
    return os.environ.get('FIREBASE_SIMULATION', 'false').lower() == 'true'

# PREDEFINED_ADMINS contains the email addresses that are allowed to access the system
# Add your administrator email addresses here
PREDEFINED_ADMINS = [
    "admin@example.com",
    "teacher@school.edu",
    "principal@school.edu"
]

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the Firebase ID token and extract user information
    This is used as a FastAPI dependency for protected routes
    """
    # Skip authentication in simulation mode
    if is_simulation_mode():
        logger.info("Simulation mode: Authentication bypassed")
        return {"email": "simulation@example.com", "uid": "simulation-user"}
    
    token = credentials.credentials
    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(token)
        
        # Extract user information
        uid = decoded_token.get('uid')
        email = decoded_token.get('email', '')
        
        # Check if user is in the predefined admin list
        if email not in PREDEFINED_ADMINS:
            logger.warning(f"Unauthorized access attempt from {email}")
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to access this resource"
            )
            
        logger.info(f"Authenticated user: {email}")
        return {"email": email, "uid": uid}
        
    except auth.InvalidIdTokenError:
        logger.warning("Invalid authentication token")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    except auth.ExpiredIdTokenError:
        logger.warning("Expired authentication token")
        raise HTTPException(
            status_code=401,
            detail="Expired authentication token"
        )
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )

# Function to check if a user has administrative privileges
def is_admin(user_data: dict):
    """Check if the user has administrative privileges"""
    return user_data.get('email') in PREDEFINED_ADMINS