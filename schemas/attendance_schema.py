from pydantic import BaseModel
from typing import List, Dict, Optional

class Attendance(BaseModel):
    """Schema for attendance records"""
    attendance_id: str
    student_id: str
    class_id: str
    timestamp: str  # ISO format datetime string
    status: str = "present"  # Default status

class AttendanceCreate(BaseModel):
    """Schema for creating a new attendance record"""
    student_id: str
    class_id: str
    timestamp: str  # ISO format datetime string

class AttendanceReport(BaseModel):
    """Schema for attendance report"""
    class_id: str
    class_name: str
    date: str
    total_students: int
    present_students: int
    absent_students: int
    attendance_list: List[Dict[str, str]]  # List of {student_id, name, status}