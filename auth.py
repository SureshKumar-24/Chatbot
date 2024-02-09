# server.py
from flask import Flask, redirect, request, jsonify
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import os
from google.auth.transport import requests
from googleapiclient.discovery import build

app = Flask(__name__)

# Google OAuth2 configuration
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
GOOGLE_CLIENT_ID = "625209807267-euphs04069u6qapidq28m5p1icool5cb.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
REDIRECT_URI ="http://localhost:3000/callback"
SCOPES = ['https://www.googleapis.com/auth/calendar']

flow = Flow.from_client_secrets_file(
    'token5.json',
    scopes=SCOPES,
    redirect_uri=REDIRECT_URI
)

# Home route
@app.route('/')
def index():
    return '''
    <h1>Google Calendar Events</h1>
    <button onclick="signIn()">Sign In with Google1</button>
    <script>
        function signIn() {
            window.location.href = '/auth/google';
        }
    </script>
    '''

# Google OAuth2 authentication route
@app.route('/auth/google')
def auth_google():
    authorization_url, _ = flow.authorization_url()
    return redirect(authorization_url)

# Google OAuth2 callback route
@app.route('/callback')
def auth_google_callback():
    flow.fetch_token(code=request.args.get('code'))
    return redirect('/calendar_events')

# Fetch Google Calendar events route
@app.route('/calendar_events')
def calendar_events():
    credentials = flow.credentials
    service = build('calendar', 'v3', credentials=credentials)
    events_result = service.events().list(calendarId='primary', timeMin='2024-01-01T00:00:00Z',
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True, port=3000)

