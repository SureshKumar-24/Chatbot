from flask import Flask, render_template, request, jsonify
import os
import pickle
import dill
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_openai import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
app = Flask(__name__)

# Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = "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"

# Define the list of URLs
urls = ['https://aws.amazon.com/what-is-aws/']

# Load data from the URLs
loaders = UnstructuredURLLoader(urls=urls)
data = loaders.load()

# Split the loaded data into documents
text_splitter = CharacterTextSplitter(separator='\n', chunk_size=1000, chunk_overlap=200)
docs = text_splitter.split_documents(data)
print(docs)

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings()

# Load or create the FAISS vector store
# Uncomment the following lines if you want to create the vector store
vectorStore_openAI = FAISS.from_documents(docs, embeddings)
with open("faiss_store_openai.pkl", "wb") as f:
    dill.dump(vectorStore_openAI, f)

# Load the vector store from a pre-saved file
with open("faiss_store_openai.pkl", "rb") as f:
    VectorStore = pickle.load(f)

# Initialize the language model and create the QA chain
llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')
chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=VectorStore.as_retriever())

@app.route('/')
def index():
    return render_template('chat.html', user_input="", bot_response="")

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']

    # Get the bot's response
    bot_response = chain({"question": user_input})["answer"]

    return jsonify({"bot_response": bot_response})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
