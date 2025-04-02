import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

class FirebaseService:
    """Service to interact with Cloud Firestore Database"""
    
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
            project_id = os.environ.get('FIREBASE_PROJECT_ID', 'fingerprint-attendance-system')
            simulation_mode = os.environ.get('FIREBASE_SIMULATION', 'false').lower() == 'true'
            
            # Log initialization details
            print(f"Initializing Firebase with credentials from: {cred_path}")
            print(f"Project ID: {project_id}")
            print(f"Simulation mode: {simulation_mode}")
            
            # Use simulation mode (no actual Firebase connection)
            if simulation_mode:
                try:
                    firebase_admin.initialize_app(options={
                        'projectId': project_id
                    })
                    print("Firebase initialized in simulation mode")
                except Exception as e:
                    print(f"Error initializing Firebase in simulation mode: {str(e)}")
            # Try to use real credentials
            elif os.path.exists(cred_path):
                try:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred, {
                        'projectId': project_id
                    })
                    print("Firebase initialized successfully with credentials file")
                except Exception as e:
                    print(f"Error initializing Firebase with credentials: {str(e)}")
                    # Fallback to simulation
                    firebase_admin.initialize_app(options={
                        'projectId': project_id
                    })
                    print("Firebase initialized in fallback simulation mode")
            else:
                # Initialize with project ID for demo purposes
                firebase_admin.initialize_app(options={
                    'projectId': project_id
                })
                print("Firebase initialized for demo (no credentials found)")
        
        # Initialize Firestore client
        self.db = firestore.client()
    
    def get_collection(self, collection_name: str):
        """Get a reference to a specific collection in Firestore"""
        return self.db.collection(collection_name)
    
    # Class operations
    def create_class(self, class_data: Dict[str, Any]) -> str:
        """Create a new class in Firestore"""
        class_id = str(uuid.uuid4())
        class_data['class_id'] = class_id
        class_data['enrolled_students'] = []
        
        # Add a new document with auto-generated ID
        self.db.collection('classes').document(class_id).set(class_data)
        
        return class_id
    
    def get_class(self, class_id: str) -> Optional[Dict[str, Any]]:
        """Get a class by ID from Firestore"""
        class_doc = self.db.collection('classes').document(class_id).get()
        
        if class_doc.exists:
            return class_doc.to_dict()
        return None
    
    def get_all_classes(self) -> Dict[str, Any]:
        """Get all classes from Firestore"""
        classes_ref = self.db.collection('classes').stream()
        classes = {}
        
        for class_doc in classes_ref:
            classes[class_doc.id] = class_doc.to_dict()
            
        return classes
    
    def update_class(self, class_id: str, class_data: Dict[str, Any]) -> bool:
        """Update a class in Firestore"""
        # Get the current data first to preserve enrolled_students
        class_doc = self.db.collection('classes').document(class_id).get()
        
        if not class_doc.exists:
            return False
        
        current_data = class_doc.to_dict()
        
        # Preserve enrolled_students field
        class_data['enrolled_students'] = current_data.get('enrolled_students', [])
        
        # Preserve class_id
        class_data['class_id'] = class_id
        
        # Update the class
        self.db.collection('classes').document(class_id).set(class_data)
        return True
    
    def delete_class(self, class_id: str) -> bool:
        """Delete a class from Firestore"""
        # Get the class first to check if it exists
        class_doc = self.db.collection('classes').document(class_id).get()
        
        if not class_doc.exists:
            return False
        
        current_data = class_doc.to_dict()
        
        # Remove enrolled_students references from each student
        enrolled_students = current_data.get('enrolled_students', [])
        for student_id in enrolled_students:
            student_doc = self.db.collection('students').document(student_id).get()
            
            if student_doc.exists:
                student_data = student_doc.to_dict()
                enrolled_classes = student_data.get('enrolled_classes', [])
                
                if class_id in enrolled_classes:
                    enrolled_classes.remove(class_id)
                    self.db.collection('students').document(student_id).update({
                        'enrolled_classes': enrolled_classes
                    })
        
        # Delete the class
        self.db.collection('classes').document(class_id).delete()
        return True
    
    # Student operations
    def create_student(self, student_data: Dict[str, Any]) -> str:
        """Create a new student in Firestore"""
        student_id = str(uuid.uuid4())
        student_data['student_id'] = student_id
        student_data['enrolled_classes'] = []
        
        # Add a new document with generated ID
        self.db.collection('students').document(student_id).set(student_data)
        
        return student_id
    
    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get a student by ID from Firestore"""
        student_doc = self.db.collection('students').document(student_id).get()
        
        if student_doc.exists:
            return student_doc.to_dict()
        return None
    
    def get_student_by_fingerprint(self, fingerprint_id: int) -> Optional[Dict[str, Any]]:
        """Get a student by fingerprint ID from Firestore"""
        # Query students collection where fingerprint_id equals the given ID
        query = self.db.collection('students').where('fingerprint_id', '==', fingerprint_id).limit(1)
        results = query.stream()
        
        # Get the first (and should be only) matching student
        for doc in results:
            return doc.to_dict()
        
        return None
    
    def get_all_students(self) -> Dict[str, Any]:
        """Get all students from Firestore"""
        students_ref = self.db.collection('students').stream()
        students = {}
        
        for student_doc in students_ref:
            students[student_doc.id] = student_doc.to_dict()
            
        return students
    
    def update_student(self, student_id: str, student_data: Dict[str, Any]) -> bool:
        """Update a student in Firestore"""
        # Get the current data first to preserve enrolled_classes
        student_doc = self.db.collection('students').document(student_id).get()
        
        if not student_doc.exists:
            return False
        
        current_data = student_doc.to_dict()
        
        # Preserve enrolled_classes field
        student_data['enrolled_classes'] = current_data.get('enrolled_classes', [])
        
        # Preserve student_id
        student_data['student_id'] = student_id
        
        # Update the student
        self.db.collection('students').document(student_id).set(student_data)
        return True
    
    def delete_student(self, student_id: str) -> bool:
        """Delete a student from Firestore"""
        # Get the student first to check if it exists
        student_doc = self.db.collection('students').document(student_id).get()
        
        if not student_doc.exists:
            return False
        
        current_data = student_doc.to_dict()
        
        # Remove student_id from enrolled_students in each class
        enrolled_classes = current_data.get('enrolled_classes', [])
        for class_id in enrolled_classes:
            class_doc = self.db.collection('classes').document(class_id).get()
            
            if class_doc.exists:
                class_data = class_doc.to_dict()
                enrolled_students = class_data.get('enrolled_students', [])
                
                if student_id in enrolled_students:
                    enrolled_students.remove(student_id)
                    self.db.collection('classes').document(class_id).update({
                        'enrolled_students': enrolled_students
                    })
        
        # Delete the student
        self.db.collection('students').document(student_id).delete()
        return True
    
    def enroll_student_in_class(self, student_id: str, class_id: str) -> bool:
        """Enroll a student in a class using Firestore"""
        # Get the student and class first to check if they exist
        student_doc = self.db.collection('students').document(student_id).get()
        class_doc = self.db.collection('classes').document(class_id).get()
        
        if not student_doc.exists or not class_doc.exists:
            return False
        
        student_data = student_doc.to_dict()
        class_data = class_doc.to_dict()
        
        # Update student's enrolled_classes
        enrolled_classes = student_data.get('enrolled_classes', [])
        if class_id not in enrolled_classes:
            enrolled_classes.append(class_id)
            self.db.collection('students').document(student_id).update({
                'enrolled_classes': enrolled_classes
            })
        
        # Update class's enrolled_students
        enrolled_students = class_data.get('enrolled_students', [])
        if student_id not in enrolled_students:
            enrolled_students.append(student_id)
            self.db.collection('classes').document(class_id).update({
                'enrolled_students': enrolled_students
            })
        
        return True
    
    # Attendance operations
    def create_attendance(self, attendance_data: Dict[str, Any]) -> str:
        """Create a new attendance record in Firestore"""
        attendance_id = str(uuid.uuid4())
        attendance_data['attendance_id'] = attendance_id
        
        # Extract date from timestamp (YYYY-MM-DD)
        timestamp = attendance_data.get('timestamp', '')
        date = timestamp.split(' ')[0]
        
        class_id = attendance_data.get('class_id')
        student_id = attendance_data.get('student_id')
        
        # Create a document ID combining class, date and student for easier querying
        document_id = f"{class_id}_{date}_{student_id}"
        
        # Store in attendance collection
        self.db.collection('attendance').document(document_id).set(attendance_data)
        
        return attendance_id
    
    def get_attendance(self, class_id: str, date: str) -> Dict[str, Any]:
        """Get attendance records for a class on a specific date from Firestore"""
        # Query attendance collection for records matching the class_id and date
        query = self.db.collection('attendance').where('class_id', '==', class_id)
        
        # Further filter for the specific date
        # In Firestore, we need to query by exact match or use compound queries
        results = query.stream()
        
        attendance_records = {}
        for doc in results:
            data = doc.to_dict()
            record_date = data.get('timestamp', '').split(' ')[0]
            
            # Filter records for the requested date
            if record_date == date:
                student_id = data.get('student_id')
                attendance_records[student_id] = data
                
        return attendance_records
    
    def get_student_attendance(self, student_id: str) -> Dict[str, Any]:
        """Get all attendance records for a student from Firestore"""
        # Query attendance collection for records where student_id matches
        query = self.db.collection('attendance').where('student_id', '==', student_id)
        results = query.stream()
        
        # Organize records by class_id and date
        student_attendance = {}
        for doc in results:
            data = doc.to_dict()
            class_id = data.get('class_id')
            timestamp = data.get('timestamp', '')
            date = timestamp.split(' ')[0]
            
            # Create nested structure
            if class_id not in student_attendance:
                student_attendance[class_id] = {}
            
            student_attendance[class_id][date] = data
        
        return student_attendance