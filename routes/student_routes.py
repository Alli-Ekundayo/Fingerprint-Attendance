from fastapi import APIRouter, HTTPException, Path, Body, Query
from typing import Dict, Any, List

from schemas.student_schema import Student, StudentCreate
from services.firebase_service import FirebaseService

# Create router
router = APIRouter(prefix="/api/students", tags=["students"])

# Initialize services
firebase_service = FirebaseService()

@router.post("/", response_model=Dict[str, str])
async def create_student(student_data: StudentCreate):
    """Create a new student"""
    try:
        student_dict = student_data.dict()
        
        # Check if fingerprint ID already exists
        existing_student = firebase_service.get_student_by_fingerprint(student_dict['fingerprint_id'])
        if existing_student:
            raise HTTPException(
                status_code=400,
                detail=f"Fingerprint ID {student_dict['fingerprint_id']} is already registered"
            )
        
        student_id = firebase_service.create_student(student_dict)
        return {"student_id": student_id, "message": "Student created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating student: {str(e)}")

@router.get("/", response_model=Dict[str, Any])
async def get_all_students():
    """Get all students"""
    try:
        students = firebase_service.get_all_students()
        return {"students": students}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving students: {str(e)}")

@router.get("/{student_id}", response_model=Dict[str, Any])
async def get_student(student_id: str = Path(..., description="The ID of the student to retrieve")):
    """Get a student by ID"""
    try:
        student_data = firebase_service.get_student(student_id)
        if not student_data:
            raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
        return student_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving student: {str(e)}")

@router.get("/fingerprint/{fingerprint_id}", response_model=Dict[str, Any])
async def get_student_by_fingerprint(fingerprint_id: int = Path(..., description="The fingerprint ID to look up")):
    """Get a student by fingerprint ID"""
    try:
        student_data = firebase_service.get_student_by_fingerprint(fingerprint_id)
        if not student_data:
            raise HTTPException(status_code=404, detail=f"No student found with fingerprint ID {fingerprint_id}")
        return student_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving student: {str(e)}")

@router.put("/{student_id}", response_model=Dict[str, str])
async def update_student(
    student_data: StudentCreate,
    student_id: str = Path(..., description="The ID of the student to update")
):
    """Update a student"""
    try:
        student_dict = student_data.dict()
        
        # Check if the new fingerprint ID already exists in another student
        existing_student = firebase_service.get_student_by_fingerprint(student_dict['fingerprint_id'])
        if existing_student and existing_student.get('student_id') != student_id:
            raise HTTPException(
                status_code=400,
                detail=f"Fingerprint ID {student_dict['fingerprint_id']} is already registered to another student"
            )
        
        success = firebase_service.update_student(student_id, student_dict)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
        
        return {"message": "Student updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating student: {str(e)}")

@router.delete("/{student_id}", response_model=Dict[str, str])
async def delete_student(student_id: str = Path(..., description="The ID of the student to delete")):
    """Delete a student"""
    try:
        success = firebase_service.delete_student(student_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
        
        return {"message": "Student deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting student: {str(e)}")