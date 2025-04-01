from fastapi import APIRouter, HTTPException, Path, Body, Query
from typing import Dict, Any, Optional

from schemas.attendance_schema import Attendance, AttendanceCreate
from services.attendance_service import AttendanceService

# Create router
router = APIRouter(prefix="/api/attendance", tags=["attendance"])

# Initialize services
attendance_service = AttendanceService()

@router.get("/record/{fingerprint_id}", response_model=Dict[str, Any])
async def record_attendance(fingerprint_id: int, timestamp: Optional[str] = None):
    """Record attendance for a student based on fingerprint ID"""
    try:
        result = attendance_service.record_attendance(fingerprint_id, timestamp)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording attendance: {str(e)}")

@router.post("/manual", response_model=Dict[str, Any])
async def manual_attendance(attendance_data: AttendanceCreate):
    """Manually record attendance"""
    try:
        # Convert attendance data to dict
        attendance_dict = attendance_data.dict()
        
        # Get student_id and class_id from request
        student_id = attendance_dict.get("student_id")
        class_id = attendance_dict.get("class_id")
        timestamp = attendance_dict.get("timestamp")
        
        # Validate that student and class exist
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        student = firebase_service.get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
        
        class_info = firebase_service.get_class(class_id)
        if not class_info:
            raise HTTPException(status_code=404, detail=f"Class with ID {class_id} not found")
        
        # Check if student is enrolled in this class
        if class_id not in student.get("enrolled_classes", []):
            raise HTTPException(
                status_code=400,
                detail=f"Student {student['name']} is not enrolled in class {class_info['class_name']}"
            )
        
        # Create attendance record
        attendance_data = {
            "student_id": student_id,
            "class_id": class_id,
            "timestamp": timestamp,
            "status": "present"
        }
        
        # Save attendance record
        attendance_id = firebase_service.create_attendance(attendance_data)
        
        return {
            "attendance_id": attendance_id,
            "message": "Attendance recorded successfully",
            "student_name": student["name"],
            "class_name": class_info["class_name"],
            "timestamp": timestamp
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording attendance: {str(e)}")

@router.get("/report/{class_id}", response_model=Dict[str, Any])
async def get_attendance_report(
    class_id: str = Path(..., description="The ID of the class"),
    date: str = Query(..., description="Date in YYYY-MM-DD format")
):
    """Get attendance report for a class on a specific date"""
    try:
        result = attendance_service.generate_attendance_report(class_id, date)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating attendance report: {str(e)}")

@router.get("/student/{student_id}", response_model=Dict[str, Any])
async def get_student_attendance(
    student_id: str = Path(..., description="The ID of the student")
):
    """Get attendance summary for a student"""
    try:
        result = attendance_service.get_student_attendance_summary(student_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving student attendance: {str(e)}")