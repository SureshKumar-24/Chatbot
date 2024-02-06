from flask import Flask, render_template, request, jsonify
from langchain import OpenAI
from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader, LLMPredictor, PromptHelper, ServiceContext, Document
from IPython.display import Markdown, display
import os
from PyPDF2 import PdfReader
app = Flask(__name__)

# Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = "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"

# Load PDF and extract text
pdf_file_obj = open("docs/jat.pdf", "rb")
pdf_reader = PdfReader(pdf_file_obj)
num_pages = len(pdf_reader.pages)
detected_text = ""

for page_num in range(num_pages):
    page_obj = pdf_reader.pages[page_num]
    detected_text += page_obj.extract_text() + "\n\n"

pdf_file_obj.close()

# Construct the GPTSimpleVectorIndex
directory = "index_store"
llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.5, model_name="text-davinci-003", max_tokens=2000))
prompt_helper = PromptHelper(4096, 512, 0.2, chunk_size_limit=600)
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)
gpt_index = GPTVectorStoreIndex.from_documents([detected_text], service_context=service_context)
gpt_index.save_to_disk(directory)

# Create ConversationalRetrievalChain
conv_interface = ConversationalRetrievalChain.from_llm(ChatOpenAI(temperature=0), retriever=gpt_index)

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

if __name__ == '__main__':
    app.run(debug=True, port=5001)
