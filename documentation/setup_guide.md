# ESP32 Fingerprint Attendance System - Setup Guide

This guide provides step-by-step instructions for setting up the IoT-based fingerprint attendance system using an ESP32, a fingerprint sensor, and Firebase as the backend.

## Table of Contents

1. [Hardware Requirements](#hardware-requirements)
2. [Hardware Assembly](#hardware-assembly)
3. [Software Setup](#software-setup)
4. [Firebase Configuration](#firebase-configuration)
5. [Uploading Code to ESP32](#uploading-code-to-esp32)
6. [System Operation](#system-operation)

## Hardware Requirements

- **ESP32 Development Board** (ESP32 DEVKIT V1 or similar)
- **Fingerprint Sensor** (R305 or compatible module)
- **3 LEDs** (Red, Green, Blue) for status indication (optional)
- **3 Resistors** (220Ω or 330Ω) for LEDs
- **Jumper Wires**
- **Breadboard**
- **USB Cable** for ESP32 programming
- **Power Supply** (USB or external 5V)

## Hardware Assembly

1. Connect the components according to the wiring diagram provided in `wiring_diagram.svg`

2. **ESP32 to Fingerprint Sensor Connections:**
   - ESP32 3.3V → Fingerprint Sensor VCC
   - ESP32 GND → Fingerprint Sensor GND
   - ESP32 GPIO16 (RX2) → Fingerprint Sensor TX
   - ESP32 GPIO17 (TX2) → Fingerprint Sensor RX

3. **LED Connections (if using status LEDs):**
   - ESP32 GPIO12 → 220Ω Resistor → Red LED → GND
   - ESP32 GPIO14 → 220Ω Resistor → Green LED → GND
   - ESP32 GPIO27 → 220Ω Resistor → Blue LED → GND

4. **Important Notes:**
   - Double-check all connections before powering on
   - Ensure the fingerprint sensor is properly powered (3.3V)
   - The sensor's TX connects to ESP32's RX and vice versa

## Software Setup

### 1. Install Required Software

1. **Arduino IDE:**
   - Download and install the latest version from [Arduino's website](https://www.arduino.cc/en/software)

2. **ESP32 Board Support:**
   - Open Arduino IDE
   - Go to File → Preferences
   - Add this URL to "Additional Boards Manager URLs":
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
   - Go to Tools → Board → Boards Manager
   - Search for "ESP32" and install "ESP32 by Espressif Systems"

3. **Required Libraries:**
   - Go to Tools → Manage Libraries
   - Install the following libraries:
     - "Adafruit Fingerprint Sensor Library" by Adafruit
     - "Firebase ESP32 Client" by Mobizt
     - "NTPClient" by Fabrice Weinberg
     - "Time" by Michael Margolis

### 2. Configure Arduino IDE for ESP32

1. Select your ESP32 board:
   - Tools → Board → ESP32 Arduino → ESP32 Dev Module
   
2. Select the correct port:
   - Tools → Port → *select the port your ESP32 is connected to*
   
3. Set upload speed (optional):
   - Tools → Upload Speed → 921600

## Firebase Configuration

### 1. Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Enter a project name and follow the setup wizard
4. Enable Google Analytics if desired

### 2. Set Up Realtime Database

1. From the Firebase console, go to "Build" → "Realtime Database"
2. Click "Create Database"
3. Choose a region closest to your location
4. Start in **test mode** for now (we'll secure it later)

### 3. Get Firebase Credentials

1. In your Firebase project, go to Project Settings (gear icon)
2. Under "General" tab, scroll down to "Your apps"
3. Click on the web app icon (</>)
4. Register a new app if needed
5. Note down the Firebase configuration details:
   - `apiKey`
   - `authDomain`
   - `databaseURL` - This is the most important for our application
   - `projectId`
   - `storageBucket`
   - `messagingSenderId`
   - `appId`

### 4. Set Up Database Security Rules

1. In the Firebase console, go to "Build" → "Realtime Database" → "Rules" tab
2. Update the rules according to your security needs. For example:
   ```json
   {
     "rules": {
       "attendance": {
         ".read": "auth.uid != null",
         ".write": "auth.uid != null"
       }
     }
   }
   ```
3. Click "Publish"

## Uploading Code to ESP32

1. **Open the Arduino Sketch:**
   - Open the Arduino IDE
   - Open the `fingerprint_attendance_system.ino` file

2. **Update WiFi and Firebase Settings:**
   - Change the WiFi SSID and password to match your network
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```
   
   - Update the Firebase host and authentication token with your project details
   ```cpp
   #define FIREBASE_HOST "your-project-id.firebaseio.com"
   #define FIREBASE_AUTH "your-firebase-database-secret"
   ```

3. **Adjust NTP Settings (if needed):**
   - If your timezone is different, change the time offset in the code
   ```cpp
   timeClient.setTimeOffset(0); // Set your time zone offset in seconds
   ```

4. **Connect ESP32 to Computer:**
   - Connect the ESP32 to your computer using a USB cable
   - Ensure the correct port is selected in Arduino IDE

5. **Upload the Code:**
   - Click the "Upload" button in Arduino IDE
   - Wait for the code to compile and upload to the ESP32
   - If you encounter errors, check the "Troubleshooting" section

6. **Verify Upload:**
   - Open the Serial Monitor (Tools → Serial Monitor)
   - Set the baud rate to 115200
   - You should see initialization messages from the ESP32

## System Operation

### 1. Enrolling Fingerprints

1. Open the Serial Monitor at 115200 baud
2. Type `enroll:1` and press Enter to enroll the first fingerprint
   - This will start enrollment mode for ID #1
3. Follow the prompts in the Serial Monitor:
   - Place your finger on the sensor when instructed
   - Remove and place again for the second scan
4. If enrollment is successful, you'll see a confirmation message
5. To enroll more fingerprints, send another command like `enroll:2` for the second user

### 2. Verifying Fingerprints (Normal Operation)

1. Type `verify` in the Serial Monitor to switch to verification mode
2. The system will continuously scan for fingerprints
3. When a recognized fingerprint is detected:
   - The green LED will blink (if connected)
   - The fingerprint ID and timestamp will be uploaded to Firebase
   - A confirmation message will appear in the Serial Monitor

### 3. Viewing Attendance Records

1. Go to your Firebase console
2. Navigate to "Realtime Database"
3. You'll see attendance records organized by date and user ID
4. Each record contains:
   - User ID (fingerprint ID)
   - Timestamp
   - Status (present)

### 4. LED Indicators

- **Red LED**: Error or failed operation
- **Green LED**: Success or confirmed operation
- **Blue LED**: Processing or system active

## Maintenance and Updates

1. **Adding New Users:**
   - Send the `enroll:ID` command through Serial Monitor
   - Use the next available ID number

2. **Clearing Fingerprint Database:**
   - To clear all fingerprints from the sensor, use the following code snippet in a separate sketch:
   ```cpp
   finger.emptyDatabase();
   ```

3. **Firmware Updates:**
   - Regularly check for updates to the libraries used
   - Update the ESP32 firmware if new versions become available

4. **Battery Considerations:**
   - If using battery power, consider implementing deep sleep functionality
   - Add code to monitor battery levels if applicable
