#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Adafruit_Fingerprint.h>
#include <Wire.h>
 #include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// WiFi Configuration
const char* ssid = "YourWiFiSSID";
const char* password = "YourWiFiPassword";

// API Configuration
const String serverAddress = "http://your-server-address:5000";
const String apiKey = "your-api-key"; // Optional, if you've configured authentication

// Hardware Configuration
#define FINGERPRINT_RX 16  // ESP32 GPIO pin connected to fingerprint sensor TX
#define FINGERPRINT_TX 17  // ESP32 GPIO pin connected to fingerprint sensor RX

// Optional RGB LED for status indication
#define LED_RED_PIN   25
#define LED_GREEN_PIN 26
#define LED_BLUE_PIN  27

// Use hardware serial for ESP32 (alternative is software serial for Arduino)
HardwareSerial fingerprintSerial(2);  // UART2 on ESP32
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&fingerprintSerial);

// Operating mode flags
bool enrollMode = false;
int enrollId = 0;
int enrollStep = 0;

// Function prototypes
void setupWiFi();
void setupFingerprint();
void setupLED();
void setupDisplay();
bool checkConnection();
void setLED(uint8_t r, uint8_t g, uint8_t b);
void displayMessage(const String& line1, const String& line2 = "", const String& line3 = "");
int getFingerprintID();
int enrollFingerprint();
bool sendAttendanceData(int fingerprintId);

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  while (!Serial);  // For Leonardo/Micro/Zero
  
  Serial.println("\n\nFingerprint Attendance System");
  Serial.println("------------------------------");
  
  // Setup LED pins
  setupLED();
  
  // Setup OLED display
  // setupDisplay();
  
  // Connect to WiFi
  setupWiFi();
  
  // Initialize fingerprint sensor
  setupFingerprint();
  
  Serial.println("System ready!");
  setLED(0, 0, 255);  // Blue for ready state
}

void loop() {
  // Check if we have a valid WiFi connection
  if (!checkConnection()) {
    Serial.println("Connection lost, attempting to reconnect...");
    setupWiFi();
    delay(5000);
    return;
  }
  
  // Check for serial commands
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("enroll ")) {
      // Extract fingerprint ID from command
      enrollId = command.substring(7).toInt();
      
      if (enrollId > 0 && enrollId <= 127) {
        enrollMode = true;
        enrollStep = 0;
        Serial.print("Starting enrollment for ID #");
        Serial.println(enrollId);
        displayMessage("Enrollment Mode", "ID: " + String(enrollId), "Place finger");
      } else {
        Serial.println("Invalid ID. Use a number between 1-127.");
      }
    }
    else if (command == "scan") {
      Serial.println("Scanning for fingerprint...");
      displayMessage("Scan Mode", "Place finger", "to record attendance");
    }
  }
  
  // Handle fingerprint enrollment
  if (enrollMode) {
    int result = enrollFingerprint();
    
    if (result == FINGERPRINT_OK) {
      // Enrollment successful
      enrollMode = false;
      Serial.println("Enrollment completed!");
      displayMessage("Enrollment", "Completed!", "ID: " + String(enrollId));
      setLED(0, 255, 0);  // Green for success
      delay(2000);
      setLED(0, 0, 255);  // Back to blue for ready state
    }
    else if (result == FINGERPRINT_NOFINGER) {
      // Waiting for finger
      // Do nothing, just wait
    }
    else if (result < 0) {
      // Enrollment failed
      enrollMode = false;
      Serial.print("Enrollment failed with error: ");
      Serial.println(result);
      displayMessage("Enrollment", "Failed!", "Error: " + String(result));
      setLED(255, 0, 0);  // Red for error
      delay(2000);
      setLED(0, 0, 255);  // Back to blue for ready state
    }
  }
  // Regular fingerprint scanning mode
  else {
    int fingerprintId = getFingerprintID();
    
    if (fingerprintId > 0) {
      Serial.print("Found fingerprint ID #");
      Serial.println(fingerprintId);
      
      // Set LED to purple while processing
      setLED(128, 0, 128);
      
      displayMessage("Fingerprint", "ID: " + String(fingerprintId), "Recording...");
      
      // Send attendance data to server
      bool success = sendAttendanceData(fingerprintId);
      
      if (success) {
        Serial.println("Attendance recorded successfully!");
        displayMessage("Attendance", "Recorded!", "ID: " + String(fingerprintId));
        setLED(0, 255, 0);  // Green for success
      } else {
        Serial.println("Failed to record attendance.");
        displayMessage("Error", "Failed to record", "attendance");
        setLED(255, 0, 0);  // Red for error
      }
      
      delay(2000);
      setLED(0, 0, 255);  // Back to blue for ready state
    }
  }
  
  delay(100);  // Short delay to prevent CPU hogging
}

void setupWiFi() {
  Serial.println("Connecting to WiFi...");
  displayMessage("Connecting", "to WiFi...", ssid);
  
  setLED(255, 165, 0);  // Orange for connecting
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    displayMessage("WiFi Connected", WiFi.localIP().toString(), "");
    setLED(0, 255, 0);  // Green for success
  } else {
    Serial.println("\nFailed to connect to WiFi!");
    displayMessage("WiFi Error", "Failed to connect", "Check credentials");
    setLED(255, 0, 0);  // Red for error
  }
  
  delay(1000);
}

void setupFingerprint() {
  Serial.println("Initializing fingerprint sensor...");
  displayMessage("Initializing", "Fingerprint", "Sensor...");
  
  fingerprintSerial.begin(57600, SERIAL_8N1, FINGERPRINT_RX, FINGERPRINT_TX);
  
  if (finger.verifyPassword()) {
    Serial.println("Fingerprint sensor found!");
    
    // Get sensor parameters
    uint8_t p = finger.getParameters();
    if (p == FINGERPRINT_OK) {
      Serial.print("Status: 0x"); Serial.println(finger.status_reg, HEX);
      Serial.print("Sys ID: 0x"); Serial.println(finger.system_id, HEX);
      Serial.print("Capacity: "); Serial.println(finger.capacity);
      Serial.print("Security level: "); Serial.println(finger.security_level);
      Serial.print("Device address: "); Serial.println(finger.device_addr, HEX);
      Serial.print("Packet size: "); Serial.println(finger.packet_len);
    }
    
    displayMessage("Sensor Ready", "Capacity: " + String(finger.capacity), "");
  } else {
    Serial.println("Fingerprint sensor not found!");
    displayMessage("Sensor Error", "Not found!", "Check connections");
    setLED(255, 0, 0);  // Red for error
    while (1) { delay(1000); }  // Halt
  }
}

void setupLED() {
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(LED_BLUE_PIN, OUTPUT);
  
  // Turn off LED initially
  setLED(0, 0, 0);
}

void setupDisplay() {
  // Uncomment if using an OLED display
  /*
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    return;
  }
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println(F("Fingerprint System"));
  display.display();
  */
}

bool checkConnection() {
  return WiFi.status() == WL_CONNECTED;
}

void setLED(uint8_t r, uint8_t g, uint8_t b) {
  // Note: Depending on your LED type (common anode vs common cathode)
  // you might need to invert the values (255-r, 255-g, 255-b)
  
  analogWrite(LED_RED_PIN, r);
  analogWrite(LED_GREEN_PIN, g);
  analogWrite(LED_BLUE_PIN, b);
}

void displayMessage(const String& line1, const String& line2, const String& line3) {
  // Print to serial for debugging
  Serial.println(line1);
  if (line2.length() > 0) Serial.println(line2);
  if (line3.length() > 0) Serial.println(line3);
  
  // Uncomment if using an OLED display
  /*
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  
  display.setCursor(0, 0);
  display.println(line1);
  
  if (line2.length() > 0) {
    display.setCursor(0, 16);
    display.println(line2);
  }
  
  if (line3.length() > 0) {
    display.setCursor(0, 32);
    display.println(line3);
  }
  
  display.display();
  */
}

int getFingerprintID() {
  uint8_t p = finger.getImage();
  if (p != FINGERPRINT_OK) {
    return -1;
  }

  p = finger.image2Tz();
  if (p != FINGERPRINT_OK) {
    return -2;
  }

  p = finger.fingerFastSearch();
  if (p != FINGERPRINT_OK) {
    return -3;
  }
  
  // Found a match!
  return finger.fingerID;
}

int enrollFingerprint() {
  int p = -1;
  
  switch (enrollStep) {
    case 0:  // Wait for the first fingerprint scan
      Serial.println("Place finger on sensor...");
      displayMessage("Enrollment", "Place finger", "on sensor");
      
      p = finger.getImage();
      if (p == FINGERPRINT_OK) {
        Serial.println("Image taken");
        
        p = finger.image2Tz(1);
        if (p == FINGERPRINT_OK) {
          Serial.println("Image converted");
          Serial.println("Remove finger");
          displayMessage("Enrollment", "Remove finger", "");
          
          delay(2000);
          enrollStep = 1;
        } else {
          Serial.println("Image conversion failed");
          return p;
        }
      }
      return p;
      
    case 1:  // Wait for finger to be removed
      p = finger.getImage();
      if (p == FINGERPRINT_NOFINGER) {
        Serial.println("Place same finger again...");
        displayMessage("Enrollment", "Place same", "finger again");
        
        enrollStep = 2;
      }
      return FINGERPRINT_NOFINGER;
      
    case 2:  // Wait for the second fingerprint scan
      p = finger.getImage();
      if (p == FINGERPRINT_OK) {
        Serial.println("Image taken");
        
        p = finger.image2Tz(2);
        if (p == FINGERPRINT_OK) {
          Serial.println("Image converted");
          
          // Create the model
          p = finger.createModel();
          if (p == FINGERPRINT_OK) {
            Serial.println("Prints matched!");
            
            // Store the model
            p = finger.storeModel(enrollId);
            if (p == FINGERPRINT_OK) {
              Serial.println("Stored!");
              return FINGERPRINT_OK;
            } else {
              Serial.println("Error storing model");
              return p;
            }
          } else {
            Serial.println("Prints did not match");
            return p;
          }
        } else {
          Serial.println("Image conversion failed");
          return p;
        }
      }
      return p;
  }
  
  return FINGERPRINT_NOFINGER;
}

bool sendAttendanceData(int fingerprintId) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("No WiFi connection");
    return false;
  }
  
  HTTPClient http;
  
  // URL for recording attendance
  String url = serverAddress + "/api/attendance/record/" + String(fingerprintId);
  
  Serial.print("Sending attendance data to: ");
  Serial.println(url);
  
  http.begin(url);
  
  // Add headers if authentication is configured
  if (apiKey.length() > 0) {
    http.addHeader("X-API-Key", apiKey);
  }
  
  // Send the request
  int httpResponseCode = http.GET();
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    
    // Parse JSON response
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, response);
    
    if (error) {
      Serial.print("deserializeJson() failed: ");
      Serial.println(error.c_str());
      http.end();
      return false;
    }
    
    // Process response data
    if (httpResponseCode == 200) {
      String studentName = doc["name"].as<String>();
      String className = doc["class_name"].as<String>();
      
      Serial.print("Recorded attendance for: ");
      Serial.println(studentName);
      Serial.print("Class: ");
      Serial.println(className);
      
      displayMessage("Attendance", studentName, className);
      
      http.end();
      return true;
    } else {
      // Error details should be in the response
      String errorMsg = doc["detail"].as<String>();
      Serial.print("Error: ");
      Serial.println(errorMsg);
      
      displayMessage("Error", errorMsg, "");
      
      http.end();
      return false;
    }
  } else {
    Serial.print("Error sending HTTP request. Code: ");
    Serial.println(httpResponseCode);
    
    displayMessage("HTTP Error", "Code: " + String(httpResponseCode), "");
    
    http.end();
    return false;
  }
}