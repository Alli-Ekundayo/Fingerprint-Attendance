from pydantic import BaseModel
from typing import List, Optional

class Student(BaseModel):
    """Schema for student information"""
    student_id: str
    name: str
    fingerprint_id: int  # ID stored in the fingerprint sensor
    enrolled_classes: List[str] = []  # List of class_ids the student is enrolled in

class StudentCreate(BaseModel):
    """Schema for creating a new student"""
    name: str
    fingerprint_id: int