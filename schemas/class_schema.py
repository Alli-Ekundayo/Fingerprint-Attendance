from pydantic import BaseModel
from typing import List, Optional

class ClassSchedule(BaseModel):
    """Schema for class schedule times"""
    day_of_week: str
    start_time: str  # Format: "HH:MM"
    end_time: str    # Format: "HH:MM"
    room_number: str

class Class(BaseModel):
    """Schema for class information"""
    class_id: str
    class_name: str
    lecturer: str
    schedules: List[ClassSchedule]
    enrolled_students: List[str] = []  # List of student IDs enrolled in this class

class ClassCreate(BaseModel):
    """Schema for creating a new class"""
    class_name: str
    lecturer: str
    schedules: List[ClassSchedule]