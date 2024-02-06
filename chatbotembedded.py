from flask import Flask, render_template, request, jsonify
import openai
import os
import fitz  # PyMuPDF

os.environ['OPENAI_API_KEY'] = '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'  # Set your OpenAI API key

# Function to split text into chunks
def chunk_text(text, chunk_size=2000):
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

# Function to extract text from a PDF document
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()
    return text

# Load the document content from a PDF
pdf_path = "docs/jat.pdf"
document_content = extract_text_from_pdf(pdf_path)
document_chunks = chunk_text(document_content)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('chat.html', user_input="", bot_response="")

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']

    # Set the system message to guide the model for document-related questions
    system_message = {'role': 'system', 'content': 'You answer questions about the document.'}

    # Include the system message, user input, and document chunks in the conversation
    messages = [
        system_message,
        {'role': 'user', 'content': user_input}
    ]

    # Concatenate document chunks directly into the assistant's message content
    assistant_message = {'role': 'assistant', 'content': '\n\n'.join(document_chunks)}
    messages.append(assistant_message)

    # Get the bot's response using OpenAI GPT-3.5-turbo model
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0
        )

        # Extract the bot's response from the API response
        bot_response = response['choices'][0]['message']['content']

    except Exception as e:
        # Handle API request errors
        bot_response = f"An error occurred: {str(e)}"

    return jsonify({"bot_response": bot_response})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
