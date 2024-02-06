from flask import Flask, redirect, render_template, request
from google_auth_oauthlib.flow import InstalledAppFlow

# import os
# os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
print('hello')
# Set up the OAuth 2.0 flow
flow = InstalledAppFlow.from_client_secrets_file(
    'token4.json',
    scopes=['https://www.googleapis.com/auth/calendar.events'],
    redirect_uri='https://enactbot.duckdns.org/callback'
)

@app.route("/")
def index():
    return render_template('index.html')  # Use render_template method

@app.route("/auth")
def authenticate():
    auth_url, _ = flow.authorization_url(prompt='consent')
    print('auth_url',auth_url);
    return redirect(auth_url)

print('hello');

@app.route("/callback")
def callback():
    auth_response = request.args.get('code')
    flow.fetch_token(authorization_response=auth_response)
    return "Authentication successful! You can close this window."

if __name__ == "__main__":
    app.run()
