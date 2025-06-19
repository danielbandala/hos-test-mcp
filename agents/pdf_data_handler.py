## this is goind to be a pdf validator agent
import os
from dotenv import load_dotenv
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Ensure the .env file is loaded to access environment variables
load_dotenv()

# Create embeddings and vector store
embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model="text-embedding-3-small"
)

def create_vector_db(pdf_path: str, persist_dir: str="db") -> Chroma:
    """
    Load a PDF file, split it into chunks, create embeddings, and store them in a vector database.
    Args:
        pdf_path (str): Path to the PDF file.
        persist_dir (str): Directory to persist the vector database.
    Returns:
        vectordb (Chroma): A vector database containing the embeddings of the PDF chunks.
    """
    # if database already exists skip the creation
    if os.path.exists(persist_dir):
        print(f"Vector database already exists at {persist_dir}. Skipping creation.")
        return Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings,
        )
    # Load the PDF file
    loader = PyPDFLoader(pdf_path, mode="single")
    docs = loader.load()  # list of Document objects
    splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    # Enrich the chunks with metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata['source'] = pdf_path
        chunk.metadata['chunk_index'] = i
        chunk.metadata['page'] = chunk.metadata.get('page', None)  # Default to None if not present
    # Create a vector database from the chunks
    vectordb = Chroma.from_documents(chunks, embeddings, persist_directory=persist_dir)
    return vectordb

def retrieve_chunks(vector_db_path:str, query: str, chunks: int=5) -> list[Document]:
    """
    Retrieve relevant chunks from the vector database based on a query.
    Args:
        query (str): The query to search for in the vector database.
        vectordb (Chroma): The vector database containing the PDF chunks.
        chunks (int): The number of relevant chunks to retrieve.
    Returns:
        results (list[Document]): A list of Document objects containing the relevant chunks.
    """
    # valdiate if the folder exists
    db_path = Path(vector_db_path)
    if not db_path.exists():
        raise FileNotFoundError(f"The vector database path {vector_db_path} does not exist.")
    # Load the vector database from the specified path
    vectordb = Chroma(
        persist_directory=vector_db_path,
        embedding_function=embeddings,
    )
    # Perform a similarity search to find relevant chunks
    results = vectordb.similarity_search(query, k=chunks)

    # filter out chunks by page number, we only want one chunk per page
    unique_page_numbers = set()
    filtered_results = []
    for doc in results:
        page_number = doc.metadata.get('page')
        if page_number not in unique_page_numbers:
            unique_page_numbers.add(page_number)
            filtered_results.append(doc)

    return results
