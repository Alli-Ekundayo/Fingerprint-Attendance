from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import pytz

from services.firebase_service import FirebaseService
from utils.time_util import get_current_time, get_day_of_week, time_in_range, format_datetime

class AttendanceService:
    """Service to handle attendance-related operations"""
    
    def __init__(self):
        """Initialize the attendance service"""
        self.firebase_service = FirebaseService()
    
    def record_attendance(self, fingerprint_id: int, timestamp: str = None) -> Dict[str, Any]:
        """
        Record attendance based on fingerprint ID
        Returns attendance data if successful, otherwise error message
        """
        # Get student by fingerprint ID
        student = self.firebase_service.get_student_by_fingerprint(fingerprint_id)
        
        if not student:
            return {"error": f"No student found with fingerprint ID: {fingerprint_id}"}
        
        # Use provided timestamp or current time
        if timestamp is None:
            current_time = get_current_time()
            timestamp = format_datetime(current_time)
        else:
            try:
                # Try to parse the timestamp to validate it
                datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return {"error": "Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS"}
        
        # Extract date from timestamp
        date = timestamp.split(' ')[0]
        
        # Extract time from timestamp
        time_str = timestamp.split(' ')[1][:5]  # HH:MM
        
        # Get current day of week
        day_of_week = get_day_of_week(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'))
        
        # Determine which class the student is currently attending
        current_class = self._determine_current_class(student, date, time_str, day_of_week)
        
        if not current_class:
            return {"error": "No class scheduled for the student at this time"}
        
        # Create attendance record
        attendance_data = {
            "student_id": student["student_id"],
            "class_id": current_class["class_id"],
            "timestamp": timestamp,
            "status": "present"
        }
        
        # Save attendance record
        attendance_id = self.firebase_service.create_attendance(attendance_data)
        
        # Return confirmation data
        return {
            "attendance_id": attendance_id,
            "student_id": student["student_id"],
            "name": student["name"],
            "class_id": current_class["class_id"],
            "class_name": current_class["class_name"],
            "timestamp": timestamp
        }
    
    def generate_attendance_report(self, class_id: str, date: str) -> Dict[str, Any]:
        """Generate attendance report for a class on a specific date"""
        # Get class information
        class_info = self.firebase_service.get_class(class_id)
        if not class_info:
            return {"error": f"No class found with ID: {class_id}"}
        
        # Get all attendance records for this class on this date
        attendance_records = self.firebase_service.get_attendance(class_id, date)
        
        # Get all enrolled students for this class
        enrolled_student_ids = class_info.get("enrolled_students", [])
        
        # Get student details
        students_data = {}
        for student_id in enrolled_student_ids:
            student = self.firebase_service.get_student(student_id)
            if student:
                students_data[student_id] = student
        
        # Create attendance list with status for each student
        attendance_list = []
        present_count = 0
        
        for student_id, student in students_data.items():
            if student_id in attendance_records:
                status = "present"
                present_count += 1
            else:
                status = "absent"
            
            attendance_list.append({
                "student_id": student_id,
                "name": student.get("name", "Unknown"),
                "status": status
            })
        
        # Sort attendance list by name
        attendance_list.sort(key=lambda x: x["name"])
        
        # Create report data
        total_students = len(enrolled_student_ids)
        absent_count = total_students - present_count
        
        report_data = {
            "class_id": class_id,
            "class_name": class_info.get("class_name", "Unknown"),
            "date": date,
            "total_students": total_students,
            "present_students": present_count,
            "absent_students": absent_count,
            "attendance_list": attendance_list
        }
        
        return report_data
    
    def get_student_attendance_summary(self, student_id: str) -> Dict[str, Any]:
        """Get attendance summary for a student"""
        # Get student information
        student = self.firebase_service.get_student(student_id)
        if not student:
            return {"error": f"No student found with ID: {student_id}"}
        
        # Get all student's attendance records
        student_attendance = self.firebase_service.get_student_attendance(student_id)
        
        # Get all classes the student is enrolled in
        enrolled_classes = student.get("enrolled_classes", [])
        
        # Initialize class attendance statistics
        class_attendance_stats = []
        
        # Get class information for each enrolled class
        for class_id in enrolled_classes:
            class_info = self.firebase_service.get_class(class_id)
            if not class_info:
                continue
            
            # Count days attended for this class
            attended_days = 0
            if class_id in student_attendance:
                attended_days = len(student_attendance[class_id])
            
            # For now, assume total days equals attended days * 2 as a placeholder
            # In a real implementation, this would be calculated based on the class schedule
            total_days = max(attended_days, 1) * 2
            
            # Calculate attendance percentage
            attendance_percentage = int((attended_days / total_days) * 100) if total_days > 0 else 0
            
            class_attendance_stats.append({
                "class_id": class_id,
                "class_name": class_info.get("class_name", "Unknown"),
                "total_days": total_days,
                "attended_days": attended_days,
                "attendance_percentage": attendance_percentage
            })
        
        # Sort by class name
        class_attendance_stats.sort(key=lambda x: x["class_name"])
        
        summary_data = {
            "student_id": student_id,
            "name": student.get("name", "Unknown"),
            "enrolled_classes": len(enrolled_classes),
            "class_attendance": class_attendance_stats
        }
        
        return summary_data
    
    def _determine_current_class(self, student: Dict[str, Any], date: str, current_time: str, day_of_week: str) -> Optional[Dict[str, Any]]:
        """
        Determine which class the student is attending based on day and time
        Returns class information if a matching class is found, otherwise None
        """
        # Get enrolled classes
        enrolled_class_ids = student.get('enrolled_classes', [])
        
        for class_id in enrolled_class_ids:
            class_info = self.firebase_service.get_class(class_id)
            
            if not class_info:
                continue
            
            # Check if the class has a schedule for today
            schedules = class_info.get('schedules', [])
            
            for schedule in schedules:
                schedule_day = schedule.get('day_of_week')
                start_time = schedule.get('start_time')
                end_time = schedule.get('end_time')
                
                if (schedule_day == day_of_week and 
                    start_time and end_time and
                    time_in_range(start_time, end_time, current_time)):
                    return class_info
        
        return None