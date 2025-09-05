from googleapiclient.discovery import build
from google.oauth2 import service_account

def create_calendar_event(service_account_file, calendar_id, summary, description, start_time, end_time, attendee_emails):
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=['https://www.googleapis.com/auth/calendar']
    )
    service = build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'UTC',
        },
        'attendees': [{'email': email} for email in attendee_emails],
        'reminders': {
            'useDefault': True,
        },
    }

    created_event = service.events().insert(
        calendarId=calendar_id,
        body=event,
        sendUpdates='all'  # Sends email invites to attendees
    ).execute()

    return created_event

# Example usage:
# create_calendar_event(
#     service_account_file='path/to/service_account.json',
#     calendar_id='primary',
#     summary='Meeting with Team',
#     description='Discuss project updates.',
#     start_time='2024-06-10T10:00:00Z',
#     end_time='2024-06-10T11:00:00Z',
#     attendee_emails=['user1@example.com', 'user2@example.com']
# )