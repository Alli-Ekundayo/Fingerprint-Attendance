from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
import os
import uvicorn
import time
import json
from datetime import datetime
import threading

# Set environment variables for simulation mode
os.environ['FIREBASE_SIMULATION'] = 'true'
os.environ['FIREBASE_DATABASE_URL'] = 'https://fingerprint-attendance-dummy.firebaseio.com'

# Import routes
from routes import class_routes, student_routes, attendance_routes

# Create FastAPI application
app = FastAPI(
    title="Fingerprint Attendance System API",
    description="API for managing classes, students, and attendance records for an IoT-based fingerprint attendance system",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(class_routes.router)
app.include_router(student_routes.router)
app.include_router(attendance_routes.router)

# Serve static files
# Create web_interface directories for CSS and JS if they don't exist
os.makedirs("web_interface/css", exist_ok=True)
os.makedirs("web_interface/js", exist_ok=True)

# Mount web_interface directories
app.mount("/css", StaticFiles(directory="web_interface/css"), name="css")
app.mount("/js", StaticFiles(directory="web_interface/js"), name="js")

# Mount static directory if it exists (for other static assets)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("web_interface/index.html", "r") as f:
        return f.read()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": app.version
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )

# Background thread for simulating fingerprint scanning
def fingerprint_scanner_simulation():
    """
    This function simulates a fingerprint scanner detecting fingerprints.
    In a real implementation, this would be replaced with actual fingerprint 
    sensor hardware integration.
    """
    from utils.fingerprint_util import FingerprintUtil
    from services.attendance_service import AttendanceService
    
    attendance_service = AttendanceService()
    fingerprint_util = FingerprintUtil()
    
    print("Starting fingerprint scanner simulation...")
    
    while True:
        # Simulate fingerprint scan every 5 seconds
        time.sleep(5)
        
        # Try to verify a fingerprint
        success, fingerprint_id = fingerprint_util.verify_fingerprint()
        
        if success and fingerprint_id is not None:
            print(f"Detected fingerprint ID: {fingerprint_id}")
            
            # Record attendance
            result = attendance_service.record_attendance(fingerprint_id)
            
            if "error" in result:
                print(f"Error recording attendance: {result['error']}")
            else:
                print(f"Attendance recorded for student: {result.get('name')}")
                print(f"Class: {result.get('class_name')}")
                print(f"Time: {result.get('timestamp')}")
        else:
            print("No fingerprint detected or not recognized")

# Entry point for running the application
if __name__ == "__main__":
    # Start fingerprint scanner simulation in a separate thread
    scanner_thread = threading.Thread(target=fingerprint_scanner_simulation, daemon=True)
    scanner_thread.start()
    
    # Run the FastAPI application
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)