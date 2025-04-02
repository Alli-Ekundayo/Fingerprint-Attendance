"""
Fingerprint management routes for the Fingerprint Attendance System API

These routes handle fingerprint enrollment, removal, and remote management
"""

from fastapi import APIRouter, HTTPException, Path, Body, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import time
from datetime import datetime

from utils.fingerprint_util import FingerprintUtil
from middleware.auth_middleware import verify_token
from services.firebase_service import FirebaseService

router = APIRouter(
    prefix="/api/fingerprints",
    tags=["fingerprints"],
    responses={404: {"description": "Not found"}},
)

# Initialize services
firebase_service = FirebaseService()
fingerprint_util = FingerprintUtil()

# Models
class FingerprintEnrollRequest(BaseModel):
    """Request model for enrolling a new fingerprint"""
    student_id: str
    fingerprint_id: Optional[int] = None
    
class FingerprintRemoveRequest(BaseModel):
    """Request model for removing a fingerprint"""
    fingerprint_id: int

class FingerprintStatusResponse(BaseModel):
    """Response model for fingerprint operations status"""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

# Endpoints
@router.post("/enroll", response_model=FingerprintStatusResponse)
async def enroll_fingerprint(
    request: FingerprintEnrollRequest,
    background_tasks: BackgroundTasks,
    user_data: Dict = Depends(verify_token)
):
    """
    Enroll a new fingerprint for a student
    
    This endpoint initiates fingerprint enrollment for a specific student. If fingerprint_id
    is not provided, the system will automatically assign the next available ID.
    """
    try:
        # Check if the student exists
        student = firebase_service.get_student(request.student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # If fingerprint_id is not provided, assign the next available ID
        fingerprint_id = request.fingerprint_id
        if fingerprint_id is None:
            # Get all students to find the next available fingerprint ID
            students = firebase_service.get_all_students()
            existing_ids = [s.get('fingerprint_id', 0) for s in students.values() if s.get('fingerprint_id')]
            fingerprint_id = 1  # Start with ID 1
            while fingerprint_id in existing_ids:
                fingerprint_id += 1
        
        # Check if the fingerprint ID is already in use by another student
        existing_student = firebase_service.get_student_by_fingerprint(fingerprint_id)
        if existing_student and existing_student.get('student_id') != request.student_id:
            raise HTTPException(
                status_code=400, 
                detail=f"Fingerprint ID {fingerprint_id} is already assigned to another student"
            )
        
        # Start enrollment in background
        def enroll_fingerprint_task():
            # This task runs in the background and communicates with the fingerprint sensor
            result = fingerprint_util.enroll_fingerprint(fingerprint_id)
            
            if result:
                # Update student's fingerprint ID in database
                if student and "name" in student and "student_id" in student:
                    firebase_service.update_student(
                        student["student_id"], 
                        {"fingerprint_id": fingerprint_id, "name": student["name"]}
                    )
                print(f"Successfully enrolled fingerprint ID {fingerprint_id} for student {student.get('name')}")
            else:
                print(f"Failed to enroll fingerprint ID {fingerprint_id} for student {student.get('name')}")
        
        # Add task to background tasks
        background_tasks.add_task(enroll_fingerprint_task)
        
        return {
            "status": "pending",
            "message": "Fingerprint enrollment initiated. Please place finger on the sensor.",
            "data": {
                "student_id": request.student_id,
                "fingerprint_id": fingerprint_id,
                "student_name": student.get("name")
            }
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrollment error: {str(e)}")

@router.post("/remove", response_model=FingerprintStatusResponse)
async def remove_fingerprint(
    request: FingerprintRemoveRequest,
    user_data: Dict = Depends(verify_token)
):
    """
    Remove a fingerprint from the system
    
    This endpoint removes a fingerprint template from the sensor and updates the student record
    """
    try:
        # Find the student with this fingerprint ID
        student = firebase_service.get_student_by_fingerprint(request.fingerprint_id)
        if not student:
            raise HTTPException(status_code=404, detail="No student found with this fingerprint ID")
        
        # Delete the fingerprint from the sensor
        result = fingerprint_util.delete_fingerprint(request.fingerprint_id)
        
        if result:
            # Update student record - set fingerprint_id to None or 0
            if student and "student_id" in student and "name" in student:
                student_id = student["student_id"]
                student_name = student["name"]
                firebase_service.update_student(
                    student_id, 
                    {"fingerprint_id": 0, "name": student_name}
                )
            else:
                raise HTTPException(status_code=400, detail="Invalid student data structure")
            
            # Get student info for the response
            student_id = student.get("student_id", "unknown") 
            student_name = student.get("name", "Unknown Student")
            
            return {
                "status": "success",
                "message": f"Fingerprint ID {request.fingerprint_id} removed successfully",
                "data": {
                    "student_id": student_id,
                    "student_name": student_name
                }
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to remove fingerprint ID {request.fingerprint_id} from the sensor"
            )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Removal error: {str(e)}")

@router.get("/status", response_model=FingerprintStatusResponse)
async def fingerprint_sensor_status(user_data: Dict = Depends(verify_token)):
    """
    Get the status of the fingerprint sensor
    """
    try:
        # Check if the fingerprint sensor is connected and working
        connected = fingerprint_util.is_connected()
        
        if connected:
            # Get the number of templates stored in the sensor
            template_count = fingerprint_util.get_template_count()
            
            return {
                "status": "connected",
                "message": "Fingerprint sensor is connected and operational",
                "data": {
                    "template_count": template_count,
                    "sensor_type": fingerprint_util.get_sensor_type()
                }
            }
        else:
            return {
                "status": "disconnected",
                "message": "Fingerprint sensor is not connected or not responding",
                "data": None
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking fingerprint sensor: {str(e)}",
            "data": None
        }