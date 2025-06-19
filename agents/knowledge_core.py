## this is goind to be a pdf validator agent
import os
from dotenv import load_dotenv
from pathlib import Path

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

def retrieve_knowledge(vector_db_path:str, query: str, chunks: int=2) -> list[Document]:
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
    return results
