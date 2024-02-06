from flask import Flask, render_template, request
import os
import langchain
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.indexes.vectorstore import Chroma

# Set the OPENAI API Key
os.environ["OPENAI_API_KEY"] ="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"

# Configure whether to persist the index
PERSIST = True

app = Flask(__name__)

query = None
chat_history = []

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', query=query)

@app.route('/', methods=['POST'])
def process_query():
    global query
    global chat_history

    query = request.form['query']

    if query in ['quit', 'q', 'exit']:
        return "Goodbye!"

    # Load index from persistence or create a new one
    if PERSIST and os.path.exists("persist"):
        vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
        index = VectorStoreIndexWrapper(vectorstore=vectorstore)
    else:
        loader = TextLoader("test.txt", encoding="utf-8")

        if PERSIST:
            # Create an index with persistence
            index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory": "persist"}).from_loaders([loader])
        else:
            # Create an index without persistence
            index = VectorstoreIndexCreator().from_loaders([loader])

    # Create a conversational retrieval chain using the specified LLM model and index retriever
    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model="gpt-3.5-turbo"),
        retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
    )

    # Generate an answer using the conversational chain
    result = chain({"question": query, "chat_history": chat_history})

    # Add the query and answer to chat history
    chat_history.append((query, result['answer']))

    return render_template('index.html', query=query, result=result['answer'])

if __name__ == '__main__':
     app.run(debug=True, port=5001)
