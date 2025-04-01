"""
Local Data Service for development and testing purposes

This service provides a simple in-memory database that mimics Firebase functionality
for local development and testing without requiring actual Firebase connectivity.
"""

import uuid
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

class LocalDataService:
    """A simple in-memory database service as a Firebase alternative for testing"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one database instance"""
        if cls._instance is None:
            cls._instance = super(LocalDataService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the local database"""
        # Initialize the database structure
        self.db = {
            'classes': {},
            'students': {},
            'attendance': {}
        }
        
        # Add sample data for testing
        self._add_sample_data()
        
        print("Local database initialized with sample data")
    
    def _add_sample_data(self):
        """Add sample data to the database"""
        # Sample classes
        class_ids = {}
        
        # Mathematics 101
        math_id = str(uuid.uuid4())
        class_ids['Mathematics 101'] = math_id
        self.db['classes'][math_id] = {
            'class_id': math_id,
            'class_name': 'Mathematics 101',
            'lecturer': 'Dr. Smith',
            'schedules': [
                {
                    'day_of_week': 'Monday',
                    'start_time': '09:00',
                    'end_time': '11:00',
                    'room_number': 'A101'
                },
                {
                    'day_of_week': 'Wednesday',
                    'start_time': '09:00',
                    'end_time': '11:00',
                    'room_number': 'A101'
                }
            ],
            'enrolled_students': []
        }
        
        # Computer Science 202
        cs_id = str(uuid.uuid4())
        class_ids['Computer Science 202'] = cs_id
        self.db['classes'][cs_id] = {
            'class_id': cs_id,
            'class_name': 'Computer Science 202',
            'lecturer': 'Prof. Johnson',
            'schedules': [
                {
                    'day_of_week': 'Tuesday',
                    'start_time': '13:00',
                    'end_time': '15:00',
                    'room_number': 'B205'
                },
                {
                    'day_of_week': 'Thursday',
                    'start_time': '13:00',
                    'end_time': '15:00',
                    'room_number': 'B205'
                }
            ],
            'enrolled_students': []
        }
        
        # Physics 120
        physics_id = str(uuid.uuid4())
        class_ids['Physics 120'] = physics_id
        self.db['classes'][physics_id] = {
            'class_id': physics_id,
            'class_name': 'Physics 120',
            'lecturer': 'Dr. Lee',
            'schedules': [
                {
                    'day_of_week': 'Monday',
                    'start_time': '14:00',
                    'end_time': '16:00',
                    'room_number': 'C310'
                },
                {
                    'day_of_week': 'Friday',
                    'start_time': '10:00',
                    'end_time': '12:00',
                    'room_number': 'C310'
                }
            ],
            'enrolled_students': []
        }
        
        # Sample students
        student_ids = {}
        student_data = [
            {'name': 'John Doe', 'fingerprint_id': 1},
            {'name': 'Jane Smith', 'fingerprint_id': 2},
            {'name': 'Robert Johnson', 'fingerprint_id': 3},
            {'name': 'Emily Davis', 'fingerprint_id': 4},
            {'name': 'Michael Wilson', 'fingerprint_id': 5}
        ]
        
        for student in student_data:
            student_id = str(uuid.uuid4())
            student_ids[student['name']] = student_id
            self.db['students'][student_id] = {
                'student_id': student_id,
                'name': student['name'],
                'fingerprint_id': student['fingerprint_id'],
                'enrolled_classes': []
            }
        
        # Enroll students in classes
        # All students in Mathematics 101
        for student_id in student_ids.values():
            self.db['students'][student_id]['enrolled_classes'].append(math_id)
            self.db['classes'][math_id]['enrolled_students'].append(student_id)
        
        # Some students in Computer Science 202
        cs_students = ['John Doe', 'Jane Smith', 'Robert Johnson']
        for name in cs_students:
            student_id = student_ids.get(name)
            if student_id:
                self.db['students'][student_id]['enrolled_classes'].append(cs_id)
                self.db['classes'][cs_id]['enrolled_students'].append(student_id)
        
        # Some students in Physics 120
        physics_students = ['Jane Smith', 'Emily Davis', 'Michael Wilson']
        for name in physics_students:
            student_id = student_ids.get(name)
            if student_id:
                self.db['students'][student_id]['enrolled_classes'].append(physics_id)
                self.db['classes'][physics_id]['enrolled_students'].append(student_id)
        
        # Create attendance records for today and yesterday
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday_date = datetime.now()
        # Safely go back one day, handling the case of the first day of the month
        if yesterday_date.day > 1:
            yesterday_date = yesterday_date.replace(day=yesterday_date.day-1)
        else:
            # If it's the first day of the month, go back to the last day of previous month
            if yesterday_date.month > 1:
                yesterday_date = yesterday_date.replace(month=yesterday_date.month-1)
                # Set to last day of previous month
                if yesterday_date.month in [1, 3, 5, 7, 8, 10, 12]:
                    yesterday_date = yesterday_date.replace(day=31)
                elif yesterday_date.month in [4, 6, 9, 11]:
                    yesterday_date = yesterday_date.replace(day=30)
                else:  # February
                    # Check for leap year
                    if (yesterday_date.year % 4 == 0 and yesterday_date.year % 100 != 0) or (yesterday_date.year % 400 == 0):
                        yesterday_date = yesterday_date.replace(day=29)
                    else:
                        yesterday_date = yesterday_date.replace(day=28)
            else:
                # Going back from January 1st to December 31st of previous year
                yesterday_date = yesterday_date.replace(year=yesterday_date.year-1, month=12, day=31)
        
        yesterday = yesterday_date.strftime('%Y-%m-%d')
        
        # Initialize attendance structure
        if math_id not in self.db['attendance']:
            self.db['attendance'][math_id] = {}
        if cs_id not in self.db['attendance']:
            self.db['attendance'][cs_id] = {}
        
        # Yesterday's attendance for Mathematics 101
        self.db['attendance'][math_id][yesterday] = {}
        for student_id in self.db['classes'][math_id]['enrolled_students']:
            attendance_id = str(uuid.uuid4())
            self.db['attendance'][math_id][yesterday][student_id] = {
                'attendance_id': attendance_id,
                'student_id': student_id,
                'class_id': math_id,
                'timestamp': f"{yesterday} 09:15:00",
                'status': 'present'
            }
        
        # Today's attendance for Computer Science 202
        self.db['attendance'][cs_id][today] = {}
        for student_id in self.db['classes'][cs_id]['enrolled_students']:
            attendance_id = str(uuid.uuid4())
            self.db['attendance'][cs_id][today][student_id] = {
                'attendance_id': attendance_id,
                'student_id': student_id,
                'class_id': cs_id,
                'timestamp': f"{today} 13:10:00",
                'status': 'present'
            }
    
    def get_reference(self, path: str):
        """Get a reference to a path in the database (mimics Firebase reference)"""
        # Handle paths like 'classes', 'students', 'attendance/class_id/date'
        parts = path.split('/')
        
        class LocalReference:
            def __init__(self, db, path_parts):
                self.db = db
                self.path_parts = path_parts
            
            def get(self):
                """Get data from the reference path"""
                if not self.path_parts:
                    return None
                
                curr = self.db
                for part in self.path_parts:
                    if not curr or part not in curr:
                        return None
                    curr = curr[part]
                
                return curr
            
            def set(self, value):
                """Set data at the reference path"""
                if not self.path_parts:
                    return False
                
                *parent_parts, last_part = self.path_parts
                
                # Navigate to parent
                parent = self.db
                for part in parent_parts:
                    if part not in parent:
                        parent[part] = {}
                    parent = parent[part]
                
                # Set value
                parent[last_part] = value
                return True
            
            def update(self, value):
                """Update data at the reference path"""
                current = self.get()
                if current is None:
                    self.set(value)
                else:
                    if isinstance(current, dict) and isinstance(value, dict):
                        current.update(value)
                        self.set(current)
                
                return True
            
            def delete(self):
                """Delete data at the reference path"""
                if not self.path_parts:
                    return False
                
                *parent_parts, last_part = self.path_parts
                
                # Navigate to parent
                parent = self.db
                for part in parent_parts:
                    if part not in parent:
                        return False
                    parent = parent[part]
                
                # Delete value
                if last_part in parent:
                    del parent[last_part]
                    return True
                return False
            
            def child(self, child_path):
                """Get a reference to a child path"""
                new_parts = self.path_parts + [child_path]
                return LocalReference(self.db, new_parts)
        
        return LocalReference(self.db, parts)
    
    # Class operations - mimic Firebase service
    def create_class(self, class_data: Dict[str, Any]) -> str:
        """Create a new class in the database"""
        class_id = str(uuid.uuid4())
        class_data['class_id'] = class_id
        class_data['enrolled_students'] = []
        
        classes_ref = self.get_reference('classes')
        classes_ref.child(class_id).set(class_data)
        
        return class_id
    
    def get_class(self, class_id: str) -> Optional[Dict[str, Any]]:
        """Get a class by ID"""
        class_ref = self.get_reference(f'classes/{class_id}')
        return class_ref.get()
    
    def get_all_classes(self) -> Dict[str, Any]:
        """Get all classes"""
        classes_ref = self.get_reference('classes')
        return classes_ref.get() or {}
    
    def update_class(self, class_id: str, class_data: Dict[str, Any]) -> bool:
        """Update a class"""
        # Get the current data first to preserve enrolled_students
        class_ref = self.get_reference(f'classes/{class_id}')
        current_data = class_ref.get()
        
        if not current_data:
            return False
        
        # Preserve enrolled_students field
        class_data['enrolled_students'] = current_data.get('enrolled_students', [])
        
        # Preserve class_id
        class_data['class_id'] = class_id
        
        # Update the class
        class_ref.set(class_data)
        return True
    
    def delete_class(self, class_id: str) -> bool:
        """Delete a class"""
        # Get the class first to check if it exists
        class_ref = self.get_reference(f'classes/{class_id}')
        current_data = class_ref.get()
        
        if not current_data:
            return False
        
        # Remove enrolled_students references from each student
        enrolled_students = current_data.get('enrolled_students', [])
        for student_id in enrolled_students:
            student_ref = self.get_reference(f'students/{student_id}')
            student_data = student_ref.get()
            
            if student_data:
                enrolled_classes = student_data.get('enrolled_classes', [])
                if class_id in enrolled_classes:
                    enrolled_classes.remove(class_id)
                    student_ref.update({'enrolled_classes': enrolled_classes})
        
        # Delete the class
        class_ref.delete()
        return True
    
    # Student operations
    def create_student(self, student_data: Dict[str, Any]) -> str:
        """Create a new student in the database"""
        student_id = str(uuid.uuid4())
        student_data['student_id'] = student_id
        student_data['enrolled_classes'] = []
        
        students_ref = self.get_reference('students')
        students_ref.child(student_id).set(student_data)
        
        return student_id
    
    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get a student by ID"""
        student_ref = self.get_reference(f'students/{student_id}')
        return student_ref.get()
    
    def get_student_by_fingerprint(self, fingerprint_id: int) -> Optional[Dict[str, Any]]:
        """Get a student by fingerprint ID"""
        students_ref = self.get_reference('students')
        students = students_ref.get() or {}
        
        for student_id, student in students.items():
            if student.get('fingerprint_id') == fingerprint_id:
                return student
        
        return None
    
    def get_all_students(self) -> Dict[str, Any]:
        """Get all students"""
        students_ref = self.get_reference('students')
        return students_ref.get() or {}
    
    def update_student(self, student_id: str, student_data: Dict[str, Any]) -> bool:
        """Update a student"""
        # Get the current data first to preserve enrolled_classes
        student_ref = self.get_reference(f'students/{student_id}')
        current_data = student_ref.get()
        
        if not current_data:
            return False
        
        # Preserve enrolled_classes field
        student_data['enrolled_classes'] = current_data.get('enrolled_classes', [])
        
        # Preserve student_id
        student_data['student_id'] = student_id
        
        # Update the student
        student_ref.set(student_data)
        return True
    
    def delete_student(self, student_id: str) -> bool:
        """Delete a student"""
        # Get the student first to check if it exists
        student_ref = self.get_reference(f'students/{student_id}')
        current_data = student_ref.get()
        
        if not current_data:
            return False
        
        # Remove student_id from enrolled_students in each class
        enrolled_classes = current_data.get('enrolled_classes', [])
        for class_id in enrolled_classes:
            class_ref = self.get_reference(f'classes/{class_id}')
            class_data = class_ref.get()
            
            if class_data:
                enrolled_students = class_data.get('enrolled_students', [])
                if student_id in enrolled_students:
                    enrolled_students.remove(student_id)
                    class_ref.update({'enrolled_students': enrolled_students})
        
        # Delete the student
        student_ref.delete()
        return True
    
    def enroll_student_in_class(self, student_id: str, class_id: str) -> bool:
        """Enroll a student in a class"""
        # Get the student and class first to check if they exist
        student_ref = self.get_reference(f'students/{student_id}')
        class_ref = self.get_reference(f'classes/{class_id}')
        
        student_data = student_ref.get()
        class_data = class_ref.get()
        
        if not student_data or not class_data:
            return False
        
        # Update student's enrolled_classes
        enrolled_classes = student_data.get('enrolled_classes', [])
        if class_id not in enrolled_classes:
            enrolled_classes.append(class_id)
            student_ref.update({'enrolled_classes': enrolled_classes})
        
        # Update class's enrolled_students
        enrolled_students = class_data.get('enrolled_students', [])
        if student_id not in enrolled_students:
            enrolled_students.append(student_id)
            class_ref.update({'enrolled_students': enrolled_students})
        
        return True
    
    # Attendance operations
    def create_attendance(self, attendance_data: Dict[str, Any]) -> str:
        """Create a new attendance record in the database"""
        attendance_id = str(uuid.uuid4())
        attendance_data['attendance_id'] = attendance_id
        
        # Extract date from timestamp (YYYY-MM-DD)
        timestamp = attendance_data.get('timestamp', '')
        date = timestamp.split(' ')[0]
        
        class_id = attendance_data.get('class_id')
        student_id = attendance_data.get('student_id')
        
        # Initialize structure if needed
        if class_id not in self.db['attendance']:
            self.db['attendance'][class_id] = {}
        
        if date not in self.db['attendance'][class_id]:
            self.db['attendance'][class_id][date] = {}
        
        # Store attendance by class_id and date
        attendance_ref = self.get_reference(f'attendance/{class_id}/{date}')
        attendance_ref.child(student_id).set(attendance_data)
        
        return attendance_id
    
    def get_attendance(self, class_id: str, date: str) -> Dict[str, Any]:
        """Get attendance records for a class on a specific date"""
        attendance_ref = self.get_reference(f'attendance/{class_id}/{date}')
        return attendance_ref.get() or {}
    
    def get_student_attendance(self, student_id: str) -> Dict[str, Any]:
        """Get all attendance records for a student"""
        # Get all attendance records
        attendance_ref = self.get_reference('attendance')
        all_attendance = attendance_ref.get() or {}
        
        # Filter for the specific student
        student_attendance = {}
        
        for class_id, dates in all_attendance.items():
            for date, records in dates.items():
                if student_id in records:
                    if class_id not in student_attendance:
                        student_attendance[class_id] = {}
                    student_attendance[class_id][date] = records[student_id]
        
        return student_attendance