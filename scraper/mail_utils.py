import argparse
import base64
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText

# Define OAuth scope
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
TOKEN_FILE = "scraper/token-dssplab.json"  # File to store OAuth token

# Authenticate and manage tokens
def authenticate_gmail():
    assert os.path.exists(TOKEN_FILE), "Cannot find token file"
    return Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

# Create an email message
def create_message(to, subject, message_text):
    message = MIMEText(message_text)
    message["to"] = to
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}

# Send email
def send_email(to, subject, message_text):
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)
    message = create_message(to, subject, message_text)
    service.users().messages().send(userId="me", body=message).execute()
    print(f"Email sent to {to}")
