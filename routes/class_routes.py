from fastapi import APIRouter, HTTPException, Path, Body
from typing import Dict, Any

from schemas.class_schema import Class, ClassCreate
from services.firebase_service import FirebaseService

# Create router
router = APIRouter(prefix="/api/classes", tags=["classes"])

# Initialize services
firebase_service = FirebaseService()

@router.post("/", response_model=Dict[str, str])
async def create_class(class_data: ClassCreate):
    """Create a new class"""
    try:
        class_dict = class_data.dict()
        class_id = firebase_service.create_class(class_dict)
        return {"class_id": class_id, "message": "Class created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating class: {str(e)}")

@router.get("/", response_model=Dict[str, Any])
async def get_all_classes():
    """Get all classes"""
    try:
        classes = firebase_service.get_all_classes()
        return {"classes": classes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving classes: {str(e)}")

@router.get("/{class_id}", response_model=Dict[str, Any])
async def get_class(class_id: str = Path(..., description="The ID of the class to retrieve")):
    """Get a class by ID"""
    try:
        class_data = firebase_service.get_class(class_id)
        if not class_data:
            raise HTTPException(status_code=404, detail=f"Class with ID {class_id} not found")
        return class_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving class: {str(e)}")

@router.put("/{class_id}", response_model=Dict[str, str])
async def update_class(
    class_data: ClassCreate,
    class_id: str = Path(..., description="The ID of the class to update")
):
    """Update a class"""
    try:
        class_dict = class_data.dict()
        success = firebase_service.update_class(class_id, class_dict)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Class with ID {class_id} not found")
        
        return {"message": "Class updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating class: {str(e)}")

@router.delete("/{class_id}", response_model=Dict[str, str])
async def delete_class(class_id: str = Path(..., description="The ID of the class to delete")):
    """Delete a class"""
    try:
        success = firebase_service.delete_class(class_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Class with ID {class_id} not found")
        
        return {"message": "Class deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting class: {str(e)}")

@router.post("/{class_id}/enroll/{student_id}", response_model=Dict[str, str])
async def enroll_student(
    class_id: str = Path(..., description="The ID of the class"),
    student_id: str = Path(..., description="The ID of the student to enroll")
):
    """Enroll a student in a class"""
    try:
        success = firebase_service.enroll_student_in_class(student_id, class_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Class or student not found or already enrolled"
            )
        
        return {"message": "Student enrolled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enrolling student: {str(e)}")