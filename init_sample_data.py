"""
Sample data initializer for Fingerprint Attendance System

This script creates sample classes and students in the Firebase database.
"""

import firebase_admin
from firebase_admin import credentials, db
import uuid
import json
import os
from datetime import datetime, timedelta

# Initialize Firebase
cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase_config/credentials.json')
database_url = os.environ.get('FIREBASE_DATABASE_URL', None)

if os.path.exists(cred_path):
    try:
        cred = credentials.Certificate(cred_path)
        if database_url:
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
        else:
            firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully with credentials file")
    except Exception as e:
        print(f"Error initializing Firebase with credentials: {str(e)}")
        # Initialize without credentials for demo purposes
        firebase_admin.initialize_app()
        print("Firebase initialized without credentials for demo purposes")
else:
    firebase_admin.initialize_app()
    print("Firebase initialized without credentials for demo purposes")

# Sample classes data
SAMPLE_CLASSES = [
    {
        "class_name": "Mathematics 101",
        "lecturer": "Dr. Smith",
        "schedules": [
            {
                "day_of_week": "Monday",
                "start_time": "09:00",
                "end_time": "11:00",
                "room_number": "A101"
            },
            {
                "day_of_week": "Wednesday",
                "start_time": "09:00",
                "end_time": "11:00",
                "room_number": "A101"
            }
        ]
    },
    {
        "class_name": "Computer Science 202",
        "lecturer": "Prof. Johnson",
        "schedules": [
            {
                "day_of_week": "Tuesday",
                "start_time": "13:00",
                "end_time": "15:00",
                "room_number": "B205"
            },
            {
                "day_of_week": "Thursday",
                "start_time": "13:00",
                "end_time": "15:00",
                "room_number": "B205"
            }
        ]
    },
    {
        "class_name": "Physics 120",
        "lecturer": "Dr. Lee",
        "schedules": [
            {
                "day_of_week": "Monday",
                "start_time": "14:00",
                "end_time": "16:00",
                "room_number": "C310"
            },
            {
                "day_of_week": "Friday",
                "start_time": "10:00",
                "end_time": "12:00",
                "room_number": "C310"
            }
        ]
    }
]

# Sample students data
SAMPLE_STUDENTS = [
    {
        "name": "John Doe",
        "fingerprint_id": 1
    },
    {
        "name": "Jane Smith",
        "fingerprint_id": 2
    },
    {
        "name": "Robert Johnson",
        "fingerprint_id": 3
    },
    {
        "name": "Emily Davis",
        "fingerprint_id": 4
    },
    {
        "name": "Michael Wilson",
        "fingerprint_id": 5
    }
]

def create_sample_data():
    """Create sample classes and students in the database"""
    class_refs = {}
    student_refs = {}
    
    # Create classes
    classes_ref = db.reference('classes')
    print("Creating sample classes...")
    
    for class_data in SAMPLE_CLASSES:
        class_id = str(uuid.uuid4())
        class_data['class_id'] = class_id
        class_data['enrolled_students'] = []
        
        classes_ref.child(class_id).set(class_data)
        class_refs[class_data['class_name']] = class_id
        print(f"Created class: {class_data['class_name']} with ID: {class_id}")
    
    # Create students
    students_ref = db.reference('students')
    print("\nCreating sample students...")
    
    for student_data in SAMPLE_STUDENTS:
        student_id = str(uuid.uuid4())
        student_data['student_id'] = student_id
        student_data['enrolled_classes'] = []
        
        students_ref.child(student_id).set(student_data)
        student_refs[student_data['name']] = student_id
        print(f"Created student: {student_data['name']} with ID: {student_id}")
    
    # Enroll students in classes
    print("\nEnrolling students in classes...")
    
    # Enroll all students in Mathematics 101
    math_class_id = class_refs.get("Mathematics 101")
    for student_name, student_id in student_refs.items():
        # Update student's enrolled classes
        student_ref = students_ref.child(student_id)
        student_data = student_ref.get()
        enrolled_classes = student_data.get('enrolled_classes', [])
        enrolled_classes.append(math_class_id)
        student_ref.update({'enrolled_classes': enrolled_classes})
        
        # Update class's enrolled students
        class_ref = classes_ref.child(math_class_id)
        class_data = class_ref.get()
        enrolled_students = class_data.get('enrolled_students', [])
        enrolled_students.append(student_id)
        class_ref.update({'enrolled_students': enrolled_students})
        
        print(f"Enrolled {student_name} in Mathematics 101")
    
    # Enroll some students in Computer Science 202
    cs_class_id = class_refs.get("Computer Science 202")
    cs_students = ["John Doe", "Jane Smith", "Robert Johnson"]
    for student_name in cs_students:
        student_id = student_refs.get(student_name)
        if not student_id:
            continue
            
        # Update student's enrolled classes
        student_ref = students_ref.child(student_id)
        student_data = student_ref.get()
        enrolled_classes = student_data.get('enrolled_classes', [])
        enrolled_classes.append(cs_class_id)
        student_ref.update({'enrolled_classes': enrolled_classes})
        
        # Update class's enrolled students
        class_ref = classes_ref.child(cs_class_id)
        class_data = class_ref.get()
        enrolled_students = class_data.get('enrolled_students', [])
        enrolled_students.append(student_id)
        class_ref.update({'enrolled_students': enrolled_students})
        
        print(f"Enrolled {student_name} in Computer Science 202")
    
    # Enroll some students in Physics 120
    physics_class_id = class_refs.get("Physics 120")
    physics_students = ["Jane Smith", "Emily Davis", "Michael Wilson"]
    for student_name in physics_students:
        student_id = student_refs.get(student_name)
        if not student_id:
            continue
            
        # Update student's enrolled classes
        student_ref = students_ref.child(student_id)
        student_data = student_ref.get()
        enrolled_classes = student_data.get('enrolled_classes', [])
        enrolled_classes.append(physics_class_id)
        student_ref.update({'enrolled_classes': enrolled_classes})
        
        # Update class's enrolled students
        class_ref = classes_ref.child(physics_class_id)
        class_data = class_ref.get()
        enrolled_students = class_data.get('enrolled_students', [])
        enrolled_students.append(student_id)
        class_ref.update({'enrolled_students': enrolled_students})
        
        print(f"Enrolled {student_name} in Physics 120")
    
    # Create some sample attendance records
    print("\nCreating sample attendance records...")
    
    # Get today's date and yesterday's date
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Record attendance for Mathematics 101 yesterday
    attendance_ref = db.reference(f'attendance/{math_class_id}/{yesterday}')
    math_students = student_refs.items()  # All students are in Math class
    
    for student_name, student_id in math_students:
        # Create a timestamp for the attendance record
        timestamp = f"{yesterday} 09:15:00"
        
        # Record attendance
        attendance_data = {
            "attendance_id": str(uuid.uuid4()),
            "student_id": student_id,
            "class_id": math_class_id,
            "timestamp": timestamp,
            "status": "present"
        }
        
        attendance_ref.child(student_id).set(attendance_data)
        print(f"Recorded attendance for {student_name} in Mathematics 101 on {yesterday}")
    
    # Record attendance for Computer Science 202 today
    attendance_ref = db.reference(f'attendance/{cs_class_id}/{today}')
    
    for student_name in cs_students:
        student_id = student_refs.get(student_name)
        if not student_id:
            continue
            
        # Create a timestamp for the attendance record
        timestamp = f"{today} 13:10:00"
        
        # Record attendance
        attendance_data = {
            "attendance_id": str(uuid.uuid4()),
            "student_id": student_id,
            "class_id": cs_class_id,
            "timestamp": timestamp,
            "status": "present"
        }
        
        attendance_ref.child(student_id).set(attendance_data)
        print(f"Recorded attendance for {student_name} in Computer Science 202 on {today}")
    
    print("\nSample data created successfully!")

if __name__ == "__main__":
    create_sample_data()