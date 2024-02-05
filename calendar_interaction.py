from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Assuming you have the access token
creds = Credentials.from_authorized_user_file('token.json')
print('hello');
# Build the service object
service = build('calendar', 'v3', credentials=creds)
print('hello1');
# Create a new calendar event (as per your previous example)
event = {
    'summary': 'Meeting with Team',
    'location': 'Online',
    'description': 'Discuss project updates.',
    'start': {
        'dateTime': '2024-02-15T10:00:00',
        'timeZone': 'America/Los_Angeles',
    },
    'end': {
        'dateTime': '2024-02-15T11:00:00',
        'timeZone': 'America/Los_Angeles',
    },
}
print('hello2');
# Call the Calendar API to create the event
created_event = service.events().insert(calendarId='primary', body=event).execute()
print('Event created: %s' % (created_event.get('htmlLink')))
