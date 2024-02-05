from flask import Flask, render_template, request, jsonify, redirect, url_for
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from PyPDF2 import PdfReader
import os

app = Flask(__name__)

# Load PDF and extract text
pdf_file_obj = open("docs/jat.pdf", "rb")
pdf_reader = PdfReader(pdf_file_obj)
num_pages = len(pdf_reader.pages)
detected_text = ""

for page_num in range(num_pages):
    page_obj = pdf_reader.pages[page_num]
    detected_text += page_obj.extract_text() + "\n\n"

pdf_file_obj.close()

# Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = "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"

# Split text into documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.create_documents([detected_text])

# Build vector index
directory = "index_store"
vector_index = FAISS.from_documents(texts, OpenAIEmbeddings())
vector_index.save_local(directory)

# Load vector index and set up retriever
vector_index = FAISS.load_local(directory, OpenAIEmbeddings())
retriever = vector_index.as_retriever(search_type="similarity", search_kwargs={"k": 6})

# Create ConversationalRetrievalChain
conv_interface = ConversationalRetrievalChain.from_llm(ChatOpenAI(temperature=0), retriever=retriever)

# Store chat history
chat_history = []  # We won't use this

@app.route('/')
def index():
    return render_template('chat.html', user_input="", bot_response="")

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']

    # Print the user's input for debugging
    print(f"User Input: {user_input}")

    # Check if the user's input is related to scheduling a meeting or setting an event
    if "schedule meeting" in user_input.lower() or "set event" in user_input.lower():
        # Print a message for debugging
        print("Redirecting to authorize")
        
        # Redirect to the Google Calendar authorization URL
        return redirect(url_for('authorize'))

    # Get the bot's response
    bot_response = conv_interface({"question": user_input, "chat_history": chat_history})["answer"]

    return jsonify({"bot_response": bot_response})

## ... (previous code remains unchanged)

# Authorization route
@app.route('/authorize')
def authorize():
    flow = InstalledAppFlow.from_client_secrets_file(
        'token1.json',
        scopes=['https://www.googleapis.com/auth/calendar.events'],
        redirect_uri='http://localhost:5000/callback'
    )

    auth_url, _ = flow.authorization_url(prompt='consent')
    print(f"Authorization URL: {auth_url}")  # Print for debugging
    return render_template('authorize.html', auth_url=auth_url)

# Callback route
@app.route('/callback')
def oauth2callback():
    flow = InstalledAppFlow.from_client_secrets_file(
        'token1.json',
        scopes=['https://www.googleapis.com/auth/calendar.events'],
        redirect_uri='http://localhost:5000/callback'
    )

    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    # Now you have the OAuth 2.0 credentials
    # Use these credentials to interact with the Google Calendar API

    # Placeholder event details (replace with logic to extract details from user's input)
    event_details = {
        'title': 'Meeting with Team',
        'location': 'Office',
        'description': 'Discuss project updates.',
        'datetime': '2024-02-15T10:00:00'
    }

    # Call the function to schedule the event (replace with actual logic)
    response = schedule_event(credentials, event_details)

    return "Authentication successful! Event created: {}".format(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
