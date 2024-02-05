from flask import Flask, redirect, render_template, request
from google_auth_oauthlib.flow import InstalledAppFlow
import traceback

app = Flask(__name__)

# Set up the OAuth 2.0 flow
flow = InstalledAppFlow.from_client_secrets_file(
    'token1.json',
    scopes=['https://www.googleapis.com/auth/calendar.events'],
    redirect_uri='https://1181-2405-201-5023-4045-1c7-e01c-1a33-32bc.ngrok-free.app/callback'
)

@app.route("/")
def index():
    return render_template('index.html')  # Use render_template method

@app.route("/auth")
def authenticate():
    auth_url, _ = flow.authorization_url(prompt='consent')
    print('auth_url',auth_url)
    return redirect(auth_url)

@app.route("/callback")
def callback():
    try:
        print('Callback route reached!')
        auth_response = request.args.get('code')
        print('Auth response:', auth_response)
        flow.fetch_token(authorization_response=auth_response)
        return "Authentication successful! You can close this window."
    except Exception as e:
        print("Error in callback route:", e)
        traceback.print_exc()
        return "Error in callback route. Check server logs for details."

if __name__ == "__main__":
    app.run(port=5000)


