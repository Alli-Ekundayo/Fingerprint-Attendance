import firebase_admin
from firebase_admin import credentials, db
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

class FirebaseService:
    """Service to interact with Firebase Realtime Database"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one Firebase connection"""
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Firebase connection"""
        # Check if Firebase app is already initialized
        if not firebase_admin._apps:
            cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase_config/credentials.json')
            database_url = os.environ.get('FIREBASE_DATABASE_URL', None)
            simulation_mode = os.environ.get('FIREBASE_SIMULATION', 'false').lower() == 'true'
            
            # Log initialization details
            print(f"Initializing Firebase with credentials from: {cred_path}")
            print(f"Database URL: {database_url}")
            print(f"Simulation mode: {simulation_mode}")
            
            # Use simulation mode (no actual Firebase connection)
            if simulation_mode:
                # Create a dummy app configuration with database URL
                if not database_url:
                    database_url = "https://fingerprint-attendance-dummy.firebaseio.com"
                
                try:
                    firebase_admin.initialize_app(options={
                        'databaseURL': database_url,
                        'projectId': 'fingerprint-attendance-system'
                    })
                    print("Firebase initialized in simulation mode")
                except Exception as e:
                    print(f"Error initializing Firebase in simulation mode: {str(e)}")
            # Try to use real credentials
            elif os.path.exists(cred_path) and database_url:
                try:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred, {
                        'databaseURL': database_url
                    })
                    print("Firebase initialized successfully with credentials file")
                except Exception as e:
                    print(f"Error initializing Firebase with credentials: {str(e)}")
                    # Fallback to simulation with dummy URL
                    firebase_admin.initialize_app(options={
                        'databaseURL': "https://fingerprint-attendance-dummy.firebaseio.com",
                        'projectId': 'fingerprint-attendance-system'
                    })
                    print("Firebase initialized in fallback simulation mode")
            else:
                # Initialize with dummy URL for demo purposes
                firebase_admin.initialize_app(options={
                    'databaseURL': "https://fingerprint-attendance-dummy.firebaseio.com",
                    'projectId': 'fingerprint-attendance-system'
                })
                print("Firebase initialized with dummy URL (no credentials found)")
    
    def get_reference(self, path: str):
        """Get a reference to a specific path in the database"""
        return db.reference(path)
    
    # Class operations
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