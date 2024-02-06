from flask import Flask, render_template, request, jsonify

from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
import os
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

    # Get the bot's response
    bot_response = conv_interface({"question": user_input, "chat_history": chat_history})["answer"]

    return jsonify({"bot_response": bot_response})

if _name_ == '__main__':
    app.run(debug=True, port=5001)