import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

def get_creds(token):
    """Creates Google Credentials object from an access token."""
    return Credentials(token=token)

def fetch_email_thread(token, thread_id):
    """Fetches the full email thread."""
    try:
        creds = get_creds(token)
        service = build('gmail', 'v1', credentials=creds)
        thread = service.users().threads().get(userId='me', id=thread_id).execute()
        messages = []
        for msg in thread.get('messages', []):
            snippet = msg.get('snippet', '')
            payload = msg.get('payload', {})
            headers = payload.get('headers', [])
            
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            
            messages.append({
                'id': msg['id'],
                'snippet': snippet,
                'sender': sender,
                'subject': subject
            })
        return messages
    except Exception as e:
        logger.error(f"Error fetching thread {thread_id}: {e}")
        raise

def fetch_calendar_events(token, time_min, time_max):
    """Fetches calendar events in the given range."""
    try:
        creds = get_creds(token)
        service = build('calendar', 'v3', credentials=creds)
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=time_min, 
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result.get('items', [])
    except Exception as e:
        logger.error(f"Error fetching calendar: {e}")
        raise

def create_draft_reply(token, thread_id, recipient, subject, body):
    """Creates a draft reply implementation."""
    try:
        creds = get_creds(token)
        service = build('gmail', 'v1', credentials=creds)
        
        # Construct message (simplified)
        import base64
        from email.message import EmailMessage
        
        message = EmailMessage()
        message.set_content(body)
        message['To'] = recipient
        message['Subject'] = subject
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        create_message = {
            'message': {
                'threadId': thread_id,
                'raw': encoded_message
            }
        }
        
        draft = service.users().drafts().create(userId='me', body=create_message).execute()
        return draft
    except Exception as e:
        logger.error(f"Error creating draft: {e}")
        raise

def create_calendar_event(token, summary, start_time, end_time, attendees=None, description=""):
    """Creates a calendar event (or tentative/draft)."""
    try:
        creds = get_creds(token)
        service = build('calendar', 'v3', credentials=creds)
        
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'},
            'attendees': [{'email': email} for email in (attendees or [])],
        }
        
        # MVP Safety: Send updates 'none' to avoid spamming guests immediately if possible
        # usage of sendUpdates='none' relies on the user to review.
        created_event = service.events().insert(
            calendarId='primary',
            body=event,
            sendUpdates='none' 
        ).execute()
        return created_event
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise
