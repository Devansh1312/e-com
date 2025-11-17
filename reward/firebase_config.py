import firebase_admin
from firebase_admin import credentials, messaging
import logging
import os

# Initialize Firebase Admin SDK with your credentials
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cred_path = os.path.join(BASE_DIR, 'scanlink-db754-firebase-adminsdk-fbsvc-3af5c88e9b.json')
cred = credentials.Certificate(cred_path)

# Initialize Firebase only once
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Constants for device types
ANDROID = 1
IOS = 2

def send_push_notification(device_token, title, body, device_type, data=None):
    """
    Sends a push notification to the specified device using Firebase Cloud Messaging (FCM).
    Handles both Android and iOS devices. Skips sending if device type or device token is invalid.
    """
    try:
        # Validate device type
        if device_type not in [1, "1", 2, "2"]:
            print(f"Invalid device type: {device_type}. Skipping notification.")
            return False

        # Validate device token
        if not isinstance(device_token, str) or not device_token.strip():
            print(f"Invalid device token: {device_token}. Skipping notification.")
            return False

        # Prepare custom data for Android
        if device_type in [1, "1"]:
            data = data or {}
            data.update({
                "title": str(title) if title else "",
                "body": str(body) if body else "",
            })

        # Android configuration (optional, only used for Android devices)
        android_config = None
        try:
            if device_type in [1, "1"]:
                android_config = messaging.AndroidConfig(
                    priority="high",
                    data={str(k): str(v) for k, v in data.items()},  # Ensure all keys and values are strings
                )
        except Exception as e:
            print(f"Error in Android config: {str(e)}")

        # iOS configuration (only used for iOS devices)
        ios_config = None
        try:
            if device_type in [2, "2"]:
                ios_config = messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            alert=messaging.ApsAlert(
                                title=title,  # Set the title for the notification
                                body=body     # Set the body for the notification
                            ),
                            content_available=True,
                        ),
                        custom_data={str(k): str(v) for k, v in (data or {}).items()},  # Ensure all keys and values are strings
                    )
                )
        except Exception as e:
            print(f"Error in iOS config: {str(e)}")

        # Creating the message with either Android or iOS configuration
        message = None
        try:
            message = messaging.Message(
                token=device_token,
                android=android_config,
                apns=ios_config,
            )
        except Exception as e:
            print(f"Error creating message: {str(e)}")            
            return False

        # Send the notification
        try:
            if message:
                response = messaging.send(message)
                # print(f"Successfully sent notification to device {device_token}")
                # print(f"Notification details - Title: '{title}', Body: '{body}'")
                # print(f"Firebase response: {response}")                
                return True
        except Exception as e:
            print(f"Error sending push notification: {str(e)}")            
            return False

    except Exception as e:
        print(f"Unexpected error in send_push_notification: {str(e)}")
        return False