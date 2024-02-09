from flask import Flask, render_template, request, jsonify
import os
import re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import googleapiclient.errors
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from PyPDF2 import PdfReader

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

# Set Google Calendar credentials
creds = Credentials.from_service_account_info({
    "type": "service_account",
    "project_id": "mystical-moon-413109",
    "private_key_id": "b36b7a108318978eaae6661b566db6b253e3e7fb",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCtMNABy7/3e795\nSxzukCfOWV04ladRXX3n8o0Q1vOhla/NAInO+9I73OFYH4cFqhWfZ2TS4fTIJWkC\nFty6rVYixeUOX7eYIVjmtU/XUTm5HWtr+NGqoRkNbiW7pRhmIA9GWu3utwSMcdwX\n8gvb1R5CVozKoI3ufo1hpgj6xZiVulKInMc8lRPZhfs6xvPqMkAuBGcIyMRta7d2\n3ZcymND1Fge4dPBUyZ0S8FTMNcmzZsKUXQgEX8aQej6Ndp8zNuMLOIhITu7C+EtD\nQFqyuQXqzG66TwWeVB68GmycyEmd71NkXTr2qG14GVGBYVXhOrponqz5pEZjD8Jy\nJW1OWurdAgMBAAECggEATTNkjWBjFnEJlYpXf7ovnEp2hPokxt67eJDEs/x1RpKA\ndovmYicbfEbGBm+rUumR0OgYZ+6EHFGcwOsrAmWw7zgylhkxsDUxOUoaKHtTFULZ\ndxxHbd142uU+GaqKuT9SP8TZqd7YPrikaOIiyh/yaJTHFq3CBs1PvXbzKsG49giH\nphghKG9iZ9tqNCB4ZaBANEyuAJf/Bis0pTO7AOT6Cyf5q8eJyVsrXoLIZO098Ipd\n+RTkl2DgE6HEE09cRqNy5RJPAV0AiTBO9sx76c4bs5wDHNReYnVCcenDLXzlbwXU\nmHyNJubgGodVF7tilN9hfjds34s6BFeYqdIT64BqewKBgQDfNo/GLCMrT9gkiIG8\nWYNprttX7nR6HX5JrOeaSucDWUjRepFX6BbIqXYfgm2mf5LAddg7JFchJqohEE51\nwNjdZCKMsWKPUork+0p1QJLen1NaVj/is/K3bwpjqhf2NjKjMVyKgtcKBZJrApw1\nXei/HYgxXsFMruVtgrODvjDnqwKBgQDGoUQ7MGqppcMLdV2RxXmL92Lo/6VNyQtT\nYdfyQKByzNOSLWLnnO9txMGvWyCJQlQO/PzvpQYGwON60b9UGdu4I4ULluNh/e9O\nbVTDcDHWyD1duvruZmTrGboL6GDc6oKs+vvEgLML2SFD5DYnnPl2bl+AFm1y7Vfp\nsG+18Y3PlwKBgQDVEgE2O2Wq74G0hfXJtGzEEhzhGAdplgO6EmnWl89jG/RtuiFJ\nl4tAKrtOIrPGrpqISzWIZw0g4QafnzA2KUsaMn7kbGNXyoQ5RkLyIBzSk6X+YryD\nDCERxtZVAsXyyhOWQgVDVtgsgdsdeRVhv+3vmSIrdnbwWzc4TP5NMN0AFwKBgHzK\nWKmvE3Qd9lo+lFi+7kwnUnb8Fgi2pGzwbdF/FM7LLKkL5rWI/UvDb8QRxnE1wMXh\n369XyF950/EX0dKupEId3rqXQ6gO98gYHEblOAqupw86J+ibYA/si9xrVF+23f57\neK3OBa8N7T5QJE3i6z+ivFEmxgCMaM0i0ixG5EdlAoGAPjC4bYZLnV7K4RrF2nL4\n82lNmm/SzVDXmaMa6pCTAa0oNEwBb53H6iIp2BHfsZ3Iue+ijBRSNFpydJSy1M+Z\nl9Kv1Gt5ZAyvGUigtJT7IScjllm5C4RX0i9UNzalbvxhSMgCH7arvDDKPZhe4TZ3\nDEg3vMcvFkmev3sDkUHlmvA=\n-----END PRIVATE KEY-----\n",
    "client_email": "chatbot@mystical-moon-413109.iam.gserviceaccount.com",
    "client_id": "109668695808378266125",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/chatbot%40mystical-moon-413109.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
})
# api_key="AIzaSyCY1LvaAArI0QjNyx5KV7OrGhRQqzY4R9I"
# # Build Google Calendar API service
# calendar_service = build('calendar', 'v3', developerKey=api_key)

# # Build Google Calendar API service using OAuth2 credentials
calendar_service = build('calendar', 'v3', credentials=creds)

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


def create_google_calendar_event():
    try:
        event = {
            'summary': 'Chatbot',
            'location': 'Chandigarh, India',
            'description': 'Join us for an informative session on Generative AI Chatbots. Learn about the latest advancements in AI technology and how they are revolutionizing the way we interact with machines. Discover how generative models work and their applications in various fields. Whether you are a developer, entrepreneur, or AI enthusiast, this event is for you!',
            'start': {
                'dateTime': '2024-02-10T21:30:00+05:30',
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': '2024-02-11T05:30:00+05:30',
                'timeZone': 'Asia/Kolkata',
            },
            'recurrence': [
                'RRULE:FREQ=DAILY;COUNT=2'
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        event = calendar_service.events().insert(calendarId='suresh24.enact@gmail.com', body=event).execute()
        return event
    except googleapiclient.errors.HttpError as e:
        # Log the error or handle the error response
        print("An error occurred while creating the event:", e)
        return None  # Return None to indicate failure

@app.route('/')
def index():
    return render_template('chat.html', user_input="", bot_response="")


# @app.route('/api/chat', methods=['POST'])
# def chat():
#     user_input = request.form['user_input'] + " Don’t justify your answers. Don’t give information not mentioned in the CONTEXT INFORMATION."

#     # Check if the user input contains the command to create an event
#     if "create event" in user_input.lower():
#         # Extract event details from user input using regex
#         match = re.search(r'create event (.+?) from (.+?) to (.+?)$', user_input, re.IGNORECASE)
#         if match:
#             # Create the event in Google Calendar
#             create_google_calendar_event()
#             bot_response = "Event created successfully."
#         else:
#             bot_response = "Failed to create event. Please provide event details in the format: 'Create event [summary] from [start datetime] to [end datetime]'."

#     else:
#         # Get the bot's response
#         bot_response = conv_interface({"question": user_input, "chat_history": chat_history})["answer"]

#     return jsonify({"bot_response": bot_response})
@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input'] + " Don’t justify your answers. Don’t give information not mentioned in the CONTEXT INFORMATION."

    # Check if the user input contains terms related to creating an event
    calendar_related_terms = ["create event","event", "schedule meeting","meeting","set up appointment", "book calendar", "add to calendar"]
    if any(term in user_input.lower() for term in calendar_related_terms):
        # Create the event in Google Calendar
        create_google_calendar_event()
        bot_response = "Event created successfully."

    else:
        # Get the bot's response
        bot_response = conv_interface({"question": user_input, "chat_history": chat_history})["answer"]

    return jsonify({"bot_response": bot_response})



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
