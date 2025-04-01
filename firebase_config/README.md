# Firebase Configuration

This directory should contain your Firebase credentials and configuration files.

## Required Files

1. `credentials.json` - The service account key file for Firebase Admin SDK
   - Download this from your Firebase project settings > Service accounts > Generate new private key

## Configuration for Web Interface

For the web interface to work with Firebase Authentication, you'll need to:

1. Go to the [Firebase console](https://console.firebase.google.com/)
2. Create a new Firebase project or use an existing one
3. Enable Authentication service and set up the desired sign-in methods (email/password is used by default)
4. Add the application's URL to the "Authorized domains" in Authentication settings
5. Update the firebase configuration in the web interface with your project details:
   - Update `web_interface/index.html` with your Firebase project configuration

## Environment Variables

The following environment variables can be set in the `.env` file:

- `FIREBASE_CREDENTIALS_PATH`: Path to the credentials JSON file (default: `firebase_config/credentials.json`)
- `FIREBASE_DATABASE_URL`: URL of your Firebase Realtime Database
- `FIREBASE_SIMULATION`: Set to `true` to run in simulation mode without actual Firebase credentials
- `FIREBASE_PROJECT_ID`: Your Firebase project ID
- `FIREBASE_APP_ID`: Your Firebase app ID 
- `FIREBASE_API_KEY`: Your Firebase API key