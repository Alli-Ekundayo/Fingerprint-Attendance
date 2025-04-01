/**
 * IoT-based Fingerprint Attendance System
 * 
 * This code implements a fingerprint-based attendance system using Arduino ESP32,
 * a fingerprint sensor (R305 or similar), and Firebase for backend data storage.
 * 
 * Features:
 * - Fingerprint enrollment and verification
 * - WiFi connectivity
 * - Firebase integration for attendance logging
 * - Error handling and retry mechanisms
 * 
 * Hardware:
 * - ESP32 (ESP32 DEVKIT V1 or similar)
 * - Fingerprint Sensor (R305 or compatible module)
 * - LED indicators (optional)
 * 
 * Libraries required:
 * - Adafruit_Fingerprint library
 * - Firebase ESP32 Client by Mobizt
 * - WiFi library
 * - NTPClient for accurate time
 * 
 * Created by: AI Assistant
 * Date: 2023
 */

#include <WiFi.h>
#include <Adafruit_Fingerprint.h>
#include <FirebaseESP32.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <TimeLib.h>

// Fingerprint sensor setup
#define FINGERPRINT_RX 16 // ESP32 GPIO pin connected to fingerprint sensor TX
#define FINGERPRINT_TX 17 // ESP32 GPIO pin connected to fingerprint sensor RX

// Status LEDs (optional)
#define RED_LED 12    // Error indicator
#define GREEN_LED 14  // Success indicator
#define BLUE_LED 27   // Processing indicator

// WiFi credentials - replace with your network details
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Firebase settings - replace with your Firebase project details
#define FIREBASE_HOST "your-project-id.firebaseio.com"
#define FIREBASE_AUTH "your-firebase-database-secret"

// Declare necessary objects
HardwareSerial fingerprintSerial(2); // Using UART2 of ESP32
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&fingerprintSerial);
FirebaseData firebaseData;
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");

// Global variables
bool enrollMode = false; // Set to true to enable fingerprint enrollment
int enrollId = 1;        // ID to use for enrollment
int maxRetries = 3;      // Maximum number of retries for Firebase operations
unsigned long lastAttemptTime = 0; // For retry timing
String lastUploadedId = "";        // For tracking last uploaded fingerprint

// Function prototypes
void setupWiFi();
void setupFingerprint();
void setupFirebase();
void handleFingerprint();
uint8_t enrollFingerprint();
uint8_t verifyFingerprint();
bool uploadAttendance(int fingerprintId);
void blinkLED(int ledPin, int blinkCount);
String getCurrentDateTime();

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  Serial.println("\n\nFingerprint Attendance System");
  
  // Initialize LED pins if used
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(BLUE_LED, OUTPUT);
  
  // Turn on the blue LED during initialization
  digitalWrite(BLUE_LED, HIGH);
  
  // Setup components
  setupWiFi();
  setupFingerprint();
  setupFirebase();
  
  // Initialize time client
  timeClient.begin();
  timeClient.setTimeOffset(0); // Set your time zone offset in seconds (e.g., +5:30 = 19800)
  
  // Turn off blue LED when setup is complete
  digitalWrite(BLUE_LED, LOW);
  
  Serial.println("System ready");
}

void loop() {
  // Update NTP time
  timeClient.update();
  
  // Check if in enrollment mode
  if (enrollMode) {
    Serial.println("Enrollment mode active. Enrolling ID #" + String(enrollId));
    Serial.println("Place finger on sensor...");
    
    uint8_t enrollResult = enrollFingerprint();
    
    if (enrollResult == FINGERPRINT_OK) {
      Serial.println("Enrollment successful for ID #" + String(enrollId));
      blinkLED(GREEN_LED, 3);
      enrollId++; // Increment for next enrollment
    } else {
      Serial.println("Enrollment failed with error code: " + String(enrollResult));
      blinkLED(RED_LED, 3);
    }
    
    // Wait a moment before next enrollment
    delay(2000);
  } else {
    // Normal verification mode
    handleFingerprint();
  }
  
  // Check for serial commands (for enrollment control)
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    if (command.startsWith("enroll:")) {
      enrollMode = true;
      enrollId = command.substring(7).toInt();
      Serial.println("Switching to enrollment mode. Starting with ID #" + String(enrollId));
    } else if (command == "verify") {
      enrollMode = false;
      Serial.println("Switching to verification mode");
    }
  }
  
  // Short delay to prevent tight looping
  delay(100);
}

/**
 * Setup WiFi connection
 */
void setupWiFi() {
  Serial.println("Connecting to WiFi...");
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected");
    Serial.println("IP address: " + WiFi.localIP().toString());
    blinkLED(GREEN_LED, 2);
  } else {
    Serial.println("\nFailed to connect to WiFi. Check credentials or try again.");
    blinkLED(RED_LED, 5);
  }
}

/**
 * Setup fingerprint sensor
 */
void setupFingerprint() {
  Serial.println("Initializing fingerprint sensor...");
  
  // Start communication with the fingerprint sensor
  fingerprintSerial.begin(57600, SERIAL_8N1, FINGERPRINT_RX, FINGERPRINT_TX);
  
  if (finger.verifyPassword()) {
    Serial.println("Found fingerprint sensor!");
    
    // Get sensor parameters
    uint8_t p = finger.getParameters();
    Serial.print("Status: 0x"); Serial.println(p, HEX);
    Serial.print("Fingerprint capacity: "); Serial.println(finger.capacity);
    
    blinkLED(GREEN_LED, 1);
  } else {
    Serial.println("Did not find fingerprint sensor :(");
    Serial.println("Check wiring or try resetting the ESP32");
    blinkLED(RED_LED, 3);
    while (1) { delay(1000); } // Stop execution
  }
}

/**
 * Setup Firebase connection
 */
void setupFirebase() {
  Serial.println("Connecting to Firebase...");
  
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
  Firebase.reconnectWiFi(true);
  
  // Set database read timeout to 1 minute
  Firebase.setReadTimeout(firebaseData, 1000 * 60);
  // Set database write size limit
  Firebase.setwriteSizeLimit(firebaseData, "tiny");
  
  Serial.println("Firebase connection established");
}

/**
 * Handle fingerprint verification and attendance logging
 */
void handleFingerprint() {
  digitalWrite(BLUE_LED, HIGH); // Indicate processing
  
  uint8_t result = verifyFingerprint();
  
  if (result == FINGERPRINT_OK) {
    Serial.println("Fingerprint matched with ID #" + String(finger.fingerID));
    
    // Only upload if this is a different fingerprint or significant time has passed
    if (lastUploadedId != String(finger.fingerID) || millis() - lastAttemptTime > 30000) {
      if (uploadAttendance(finger.fingerID)) {
        lastUploadedId = String(finger.fingerID);
        blinkLED(GREEN_LED, 2);
      } else {
        blinkLED(RED_LED, 2);
      }
    } else {
      Serial.println("Ignoring duplicate scan within short time period");
      blinkLED(GREEN_LED, 1);
    }
    
    lastAttemptTime = millis();
  } else if (result == FINGERPRINT_NOTFOUND) {
    Serial.println("Fingerprint not found in database");
    blinkLED(RED_LED, 1);
  }
  
  digitalWrite(BLUE_LED, LOW); // Turn off processing indicator
  delay(1000); // Brief delay before next scan
}

/**
 * Enroll a new fingerprint into the sensor
 * 
 * @return Fingerprint sensor status code
 */
uint8_t enrollFingerprint() {
  int p = -1;
  
  // Phase 1: Get first fingerprint image
  Serial.println("Place finger on sensor for first scan...");
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
      case FINGERPRINT_OK:
        Serial.println("Image taken");
        break;
      case FINGERPRINT_NOFINGER:
        Serial.print(".");
        delay(100);
        break;
      case FINGERPRINT_PACKETRECIEVEERR:
        Serial.println("Communication error");
        return p;
      case FINGERPRINT_IMAGEFAIL:
        Serial.println("Imaging error");
        return p;
      default:
        Serial.println("Unknown error");
        return p;
    }
  }

  // Convert image to template
  p = finger.image2Tz(1);
  if (p != FINGERPRINT_OK) {
    Serial.println("Image conversion to template failed");
    return p;
  }

  Serial.println("Remove finger");
  delay(2000);
  p = 0;
  while (p != FINGERPRINT_NOFINGER) {
    p = finger.getImage();
  }

  // Phase 2: Get second fingerprint image
  p = -1;
  Serial.println("Place same finger again...");
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
      case FINGERPRINT_OK:
        Serial.println("Image taken");
        break;
      case FINGERPRINT_NOFINGER:
        Serial.print(".");
        delay(100);
        break;
      case FINGERPRINT_PACKETRECIEVEERR:
        Serial.println("Communication error");
        return p;
      case FINGERPRINT_IMAGEFAIL:
        Serial.println("Imaging error");
        return p;
      default:
        Serial.println("Unknown error");
        return p;
    }
  }

  // Convert second image to template
  p = finger.image2Tz(2);
  if (p != FINGERPRINT_OK) {
    Serial.println("Image conversion to template failed");
    return p;
  }

  // Create fingerprint model from two templates
  p = finger.createModel();
  if (p != FINGERPRINT_OK) {
    Serial.println("Failed to create fingerprint model");
    return p;
  }

  // Store model in sensor memory
  p = finger.storeModel(enrollId);
  if (p != FINGERPRINT_OK) {
    Serial.println("Failed to store fingerprint model");
    return p;
  }

  return FINGERPRINT_OK;
}

/**
 * Verify a fingerprint against stored templates
 * 
 * @return Fingerprint sensor status code
 */
uint8_t verifyFingerprint() {
  uint8_t p = finger.getImage();
  if (p != FINGERPRINT_OK) {
    return p;
  }

  p = finger.image2Tz();
  if (p != FINGERPRINT_OK) {
    return p;
  }

  p = finger.fingerSearch();
  if (p != FINGERPRINT_OK) {
    return p;
  }

  // Found a match
  return FINGERPRINT_OK;
}

/**
 * Upload attendance record to Firebase
 * 
 * @param fingerprintId The ID of the matched fingerprint
 * @return True if upload successful, false otherwise
 */
bool uploadAttendance(int fingerprintId) {
  String dateTime = getCurrentDateTime();
  String path = "attendance/" + dateTime.substring(0, 10) + "/" + String(fingerprintId);
  
  // Create JSON data
  FirebaseJson json;
  json.set("user_id", fingerprintId);
  json.set("timestamp", dateTime);
  json.set("status", "present");
  
  Serial.println("Uploading attendance data to Firebase...");
  
  // Try to upload with retry mechanism
  bool success = false;
  int retries = 0;
  
  while (!success && retries < maxRetries) {
    if (Firebase.setJSON(firebaseData, path, json)) {
      Serial.println("Attendance uploaded successfully!");
      success = true;
    } else {
      Serial.println("Failed to upload attendance: " + firebaseData.errorReason());
      retries++;
      if (retries < maxRetries) {
        Serial.println("Retrying... (" + String(retries) + "/" + String(maxRetries) + ")");
        delay(1000 * retries); // Increasing delay between retries
      }
    }
  }
  
  return success;
}

/**
 * Get current date and time in ISO format from NTP
 * 
 * @return Date and time string in format YYYY-MM-DD HH:MM:SS
 */
String getCurrentDateTime() {
  // Get UNIX timestamp from NTP
  unsigned long epochTime = timeClient.getEpochTime();
  
  // Convert to human-readable format
  String formattedTime = "";
  
  // Format the date: YYYY-MM-DD
  struct tm *ptm = gmtime((time_t *)&epochTime);
  char dateBuffer[11];
  sprintf(dateBuffer, "%04d-%02d-%02d", ptm->tm_year + 1900, ptm->tm_mon + 1, ptm->tm_mday);
  
  // Format the time: HH:MM:SS
  String timeString = timeClient.getFormattedTime();
  
  formattedTime = String(dateBuffer) + " " + timeString;
  return formattedTime;
}

/**
 * Blink an LED a specified number of times
 * 
 * @param ledPin GPIO pin number of the LED
 * @param blinkCount Number of times to blink
 */
void blinkLED(int ledPin, int blinkCount) {
  for (int i = 0; i < blinkCount; i++) {
    digitalWrite(ledPin, HIGH);
    delay(200);
    digitalWrite(ledPin, LOW);
    delay(200);
  }
}
