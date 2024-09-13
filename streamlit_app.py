import os
import streamlit as st
import pickle
import time
from langchain.llms import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


# Streamlit setup
st.title("Artical Research Tool 📈")
st.sidebar.title("News Article URLs")

# Collect user input for article URLs
urls = [st.sidebar.text_input(f"URL {i+1}") for i in range(2)]
process_url_clicked = st.sidebar.button("Process URLs")

# File path for saving FAISS index
file_path = "faiss_store_openai.pkl"

# Main content placeholder
main_placeholder = st.empty()
llm = OpenAI(temperature=0.9, max_tokens=1000)

if process_url_clicked:
    # Load data from provided URLs
    loader = UnstructuredURLLoader(urls=urls)
    main_placeholder.text("Data Loading...Started...✅✅✅")
    data = loader.load()

    # Split data into documents
    text_splitter = RecursiveCharacterTextSplitter(
        separators = ['\n\n', '\n', '.', ','],
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    main_placeholder.text("Text Splitter...Started...✅✅✅")
    docs = text_splitter.split_documents(data)

    # Create embeddings and save to FAISS index
    embeddings = HuggingFaceEmbeddings()
    vectorstore_openai = FAISS.from_documents(docs, embeddings)
    main_placeholder.text("Embedding Vector Started Building...✅✅✅")
    time.sleep(2)

    # Save the FAISS index to a pickle file
    with open(file_path, "wb") as f:
        pickle.dump(vectorstore_openai, f)

# User input for the question
query = main_placeholder.text_input("Question: ")

# Process the question and display the answer and sources
if query:
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            vectorstore = pickle.load(f)
            chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vectorstore.as_retriever())
            result = chain({"question": query}, return_only_outputs=True)

            # Display answer
            st.header("Answer")
            st.write(result["answer"])

            # Display sources, if available
            sources = result.get("sources", "")
            if sources:
                st.subheader("Sources:")
                sources_list = sources.split("\n")
                for source in sources_list:
                    st.write(source)
