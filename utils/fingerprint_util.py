import serial
import time
import random
from typing import Tuple, Optional, List
import os
import glob

# For CircuitPython fingerprint library
try:
    import adafruit_fingerprint
    FINGERPRINT_LIBRARY_AVAILABLE = True
except ImportError:
    print("Adafruit fingerprint library not available, using simulation mode")
    FINGERPRINT_LIBRARY_AVAILABLE = False
    # Create a stub for the constants to avoid errors
    class AdafruitFingerprintStub:
        OK = 0
        
        # Additional stub methods and attributes for simulation mode
        class FingerprintStub:
            def __init__(self):
                self.finger_id = 0
                self.confidence = 0
                self.template_count = 0
                self.model_id = 0
            
            def get_image(self):
                return AdafruitFingerprintStub.OK
                
            def image_2_tz(self, slot):
                return AdafruitFingerprintStub.OK
                
            def finger_search(self):
                return AdafruitFingerprintStub.OK
                
            def create_model(self):
                return AdafruitFingerprintStub.OK
                
            def store(self):
                return AdafruitFingerprintStub.OK
                
            def delete_model(self, model_id):
                return AdafruitFingerprintStub.OK
                
            def read_templates(self):
                return AdafruitFingerprintStub.OK
        
        @staticmethod
        def Adafruit_Fingerprint(serial_conn):
            return AdafruitFingerprintStub.FingerprintStub()
            
    adafruit_fingerprint = AdafruitFingerprintStub()

class FingerprintUtil:
    """Utility for interacting with the fingerprint sensor via serial connection"""
    
    def __init__(self, port=None, baud_rate=57600):
        """Initialize fingerprint utility"""
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self.fingerprint = None
        
        # Set up simulation mode for development/testing
        self.simulation_mode = not FINGERPRINT_LIBRARY_AVAILABLE or os.environ.get('FINGERPRINT_SIMULATION', 'true').lower() == 'true'
        
        if self.simulation_mode:
            print("Fingerprint sensor running in simulation mode")
            
            # Create sample fingerprint database for simulation
            self.simulated_fingerprints = {
                1: "John Doe",
                2: "Jane Smith",
                3: "Robert Johnson",
                4: "Emily Davis",
                5: "Michael Wilson"
            }
    
    def _get_port(self):
        """Attempt to determine the serial port for the fingerprint sensor"""
        if self.port:
            return self.port
            
        # Try to find the port automatically
        ports = []
        
        # Different patterns based on OS
        if os.name == 'nt':  # Windows
            ports = ['COM%s' % (i + 1) for i in range(256)]
        else:  # Linux/Unix
            patterns = [
                '/dev/ttyUSB*',
                '/dev/ttyACM*',
                '/dev/tty.*',
                '/dev/cu.*'
            ]
            for pattern in patterns:
                ports.extend(glob.glob(pattern))
        
        # Test each port
        for port in ports:
            try:
                s = serial.Serial(port, self.baud_rate, timeout=1)
                s.close()
                return port
            except (OSError, serial.SerialException):
                pass
                
        # If no port found, return None
        return None
    
    def connect(self) -> bool:
        """Connect to the fingerprint sensor"""
        if self.simulation_mode:
            print("Connecting to simulated fingerprint sensor")
            return True
            
        try:
            # Get port if not already specified
            if not self.port:
                self.port = self._get_port()
                
            if not self.port:
                print("No fingerprint sensor port found")
                return False
                
            # Open serial connection
            self.ser = serial.Serial(self.port, baudrate=self.baud_rate, timeout=1)
            
            # Initialize fingerprint sensor
            if FINGERPRINT_LIBRARY_AVAILABLE:
                self.fingerprint = adafruit_fingerprint.Adafruit_Fingerprint(self.ser)
                
                # Check if connection is successful by reading sensor parameters
                if self.fingerprint.read_templates() != adafruit_fingerprint.OK:
                    print("Failed to read templates from sensor")
                    self.disconnect()
                    return False
            
            print(f"Successfully connected to fingerprint sensor on {self.port}")
            return True
        except Exception as e:
            print(f"Error connecting to fingerprint sensor: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from the fingerprint sensor"""
        if self.simulation_mode:
            return
            
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.ser = None
            self.fingerprint = None
    
    def verify_fingerprint(self) -> Tuple[bool, Optional[int]]:
        """
        Verify a fingerprint against stored templates
        Returns (success, fingerprint_id)
        """
        if self.simulation_mode:
            # Simulate random fingerprint detection
            fingerprint_id = self._simulate_fingerprint_verification()
            return (fingerprint_id is not None, fingerprint_id)
        
        # Real implementation with hardware
        if not self.ser or not self.fingerprint:
            if not self.connect():
                return (False, None)
        
        try:
            if FINGERPRINT_LIBRARY_AVAILABLE:
                print("Waiting for finger...")
                
                # Check if finger is on the sensor
                if not self._wait_for_finger_present():
                    return (False, None)
                
                # Get the image
                if self.fingerprint.get_image() != adafruit_fingerprint.OK:
                    print("Failed to get fingerprint image")
                    return (False, None)
                
                # Convert image to characteristics
                if self.fingerprint.image_2_tz(1) != adafruit_fingerprint.OK:
                    print("Failed to convert image to characteristics")
                    return (False, None)
                
                # Search for the fingerprint
                if self.fingerprint.finger_search() != adafruit_fingerprint.OK:
                    print("Fingerprint not found")
                    return (False, None)
                
                # Fingerprint found
                fingerprint_id = self.fingerprint.finger_id
                confidence = self.fingerprint.confidence
                print(f"Fingerprint found with ID #{fingerprint_id} (confidence: {confidence})")
                
                # Wait for finger to be removed
                self._wait_for_finger_removed()
                
                return (True, fingerprint_id)
            else:
                print("Fingerprint library not available")
                return (False, None)
        except Exception as e:
            print(f"Error verifying fingerprint: {str(e)}")
            return (False, None)
    
    def _wait_for_finger_present(self, timeout=10) -> bool:
        """Wait for a finger to be placed on the sensor"""
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            if self.fingerprint.get_image() == adafruit_fingerprint.OK:
                return True
            time.sleep(0.1)
        print("Timeout waiting for finger")
        return False
    
    def _wait_for_finger_removed(self, timeout=10) -> bool:
        """Wait for a finger to be removed from the sensor"""
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            if self.fingerprint.get_image() != adafruit_fingerprint.OK:
                return True
            time.sleep(0.1)
        print("Timeout waiting for finger to be removed")
        return False
    
    def _simulate_fingerprint_verification(self) -> Optional[int]:
        """
        Simulate fingerprint verification for development/testing
        In a real implementation, this would be replaced with actual
        communication with the fingerprint sensor
        """
        # Random chance of a fingerprint being detected (70%)
        if random.random() < 0.7:
            # Return a random fingerprint ID from our simulated database
            fingerprint_id = random.choice(list(self.simulated_fingerprints.keys()))
            print(f"Simulated fingerprint detected: ID #{fingerprint_id} ({self.simulated_fingerprints[fingerprint_id]})")
            return fingerprint_id
        else:
            print("Simulated scenario: No fingerprint detected")
            return None
    
    def enroll_fingerprint(self, new_id: int) -> bool:
        """
        Enroll a new fingerprint in the sensor
        Returns True if enrollment successful, otherwise False
        """
        if self.simulation_mode:
            # Simulate enrollment
            return self._simulate_fingerprint_enrollment(new_id)
        
        # Real implementation with hardware
        if not self.ser or not self.fingerprint:
            if not self.connect():
                return False
        
        try:
            if FINGERPRINT_LIBRARY_AVAILABLE:
                print("Enrolling new fingerprint...")
                
                # First scan
                print("Place finger on sensor for first scan...")
                if not self._wait_for_finger_present():
                    return False
                
                if self.fingerprint.get_image() != adafruit_fingerprint.OK:
                    print("Failed to get fingerprint image")
                    return False
                
                if self.fingerprint.image_2_tz(1) != adafruit_fingerprint.OK:
                    print("Failed to convert image to characteristics")
                    return False
                
                print("Remove finger")
                if not self._wait_for_finger_removed():
                    return False
                
                # Second scan
                print("Place same finger again for second scan...")
                if not self._wait_for_finger_present():
                    return False
                
                if self.fingerprint.get_image() != adafruit_fingerprint.OK:
                    print("Failed to get fingerprint image")
                    return False
                
                if self.fingerprint.image_2_tz(2) != adafruit_fingerprint.OK:
                    print("Failed to convert image to characteristics")
                    return False
                
                # Create model
                if self.fingerprint.create_model() != adafruit_fingerprint.OK:
                    print("Failed to create fingerprint model - scans did not match")
                    return False
                
                # Store model
                self.fingerprint.model_id = new_id
                if self.fingerprint.store() != adafruit_fingerprint.OK:
                    print(f"Failed to store fingerprint with ID {new_id}")
                    return False
                
                print(f"Fingerprint enrolled successfully with ID {new_id}")
                
                # Wait for finger to be removed
                self._wait_for_finger_removed()
                
                return True
            else:
                print("Fingerprint library not available")
                return False
        except Exception as e:
            print(f"Error enrolling fingerprint: {str(e)}")
            return False
    
    def _simulate_fingerprint_enrollment(self, new_id: int) -> bool:
        """
        Simulate fingerprint enrollment for development/testing
        In a real implementation, this would be replaced with actual
        communication with the fingerprint sensor
        """
        # Simulate the enrollment process
        print(f"Simulating fingerprint enrollment for ID {new_id}")
        
        # Check if ID already exists in our simulated database
        if new_id in self.simulated_fingerprints:
            print(f"ID {new_id} already exists in the database")
            return False
        
        # Add to our simulated database with a placeholder name
        self.simulated_fingerprints[new_id] = f"User #{new_id}"
        print(f"Simulated fingerprint enrolled with ID {new_id}")
        
        return True
        
    def delete_fingerprint(self, fingerprint_id: int) -> bool:
        """
        Delete a fingerprint template from the sensor
        Returns True if deletion was successful, otherwise False
        """
        if self.simulation_mode:
            # Simulate deletion
            if fingerprint_id in self.simulated_fingerprints:
                del self.simulated_fingerprints[fingerprint_id]
                print(f"Simulated fingerprint with ID {fingerprint_id} deleted")
                return True
            else:
                print(f"Simulated fingerprint with ID {fingerprint_id} not found")
                return False
                
        # Real implementation with hardware
        if not self.ser or not self.fingerprint:
            if not self.connect():
                return False
                
        try:
            if FINGERPRINT_LIBRARY_AVAILABLE:
                # Delete the template
                if self.fingerprint.delete_model(fingerprint_id) == adafruit_fingerprint.OK:
                    print(f"Fingerprint with ID {fingerprint_id} deleted successfully")
                    return True
                else:
                    print(f"Failed to delete fingerprint with ID {fingerprint_id}")
                    return False
            else:
                print("Fingerprint library not available")
                return False
        except Exception as e:
            print(f"Error deleting fingerprint: {str(e)}")
            return False
            
    def get_template_count(self) -> int:
        """
        Get the number of fingerprint templates stored in the sensor
        """
        if self.simulation_mode:
            # Return count of simulated fingerprints
            count = len(self.simulated_fingerprints)
            print(f"Simulated fingerprint template count: {count}")
            return count
            
        # Real implementation with hardware
        if not self.ser or not self.fingerprint:
            if not self.connect():
                return 0
                
        try:
            if FINGERPRINT_LIBRARY_AVAILABLE:
                # Read the template count
                if self.fingerprint.read_templates() == adafruit_fingerprint.OK:
                    count = self.fingerprint.template_count
                    print(f"Fingerprint template count: {count}")
                    return count
                else:
                    print("Failed to read template count")
                    return 0
            else:
                print("Fingerprint library not available")
                return 0
        except Exception as e:
            print(f"Error reading template count: {str(e)}")
            return 0
            
    def is_connected(self) -> bool:
        """
        Check if the fingerprint sensor is connected and operational
        """
        if self.simulation_mode:
            return True
            
        # Try to connect if not already connected
        if not self.ser or not self.fingerprint:
            return self.connect()
            
        try:
            # Test connection by reading templates
            if FINGERPRINT_LIBRARY_AVAILABLE:
                return self.fingerprint.read_templates() == adafruit_fingerprint.OK
            return False
        except Exception:
            return False
            
    def get_sensor_type(self) -> str:
        """
        Get information about the fingerprint sensor type
        """
        if self.simulation_mode:
            return "Simulated Fingerprint Sensor"
            
        if not self.ser or not self.fingerprint:
            if not self.connect():
                return "Unknown (not connected)"
        
        try:
            # In a real implementation, we would query the sensor for its type/model
            # Since we're using a stub in many cases, we'll return a generic response
            if FINGERPRINT_LIBRARY_AVAILABLE:
                # Try to get sensor information - this is implementation specific
                # For Adafruit sensors, we can return the sensor type with some details
                return f"Adafruit Fingerprint Sensor (Baud: {self.baud_rate}, Port: {self.port or 'unknown'})"
            else:
                return "Unknown (library not available)"
        except Exception as e:
            print(f"Error getting sensor type: {str(e)}")
            return f"Unknown (error: {str(e)})"