## this is goind to be a pdf validator agent
from dotenv import load_dotenv
import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Ensure the .env file is loaded to access environment variables
load_dotenv()

def create_vectordb_from_pdf(input_pdf_path, persist_directory="db"):
    """
    Create a vector store from a PDF file.
    Args:
        input_pdf_path (str): Path to the input PDF file.
        persist_directory (str): Directory to persist the vector store.
    Returns:
        vectordb (Chroma): A vector store containing the PDF content.
    """
    loader = PyPDFLoader(input_pdf_path, mode="single")
    docs = loader.load()  # list of Document objects
    splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=400)
    chunks = splitter.split_documents(docs)

    # Create embeddings and vector store
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model="text-embedding-3-small"
    )
    vectordb = Chroma.from_documents(chunks, embeddings, persist_directory=persist_directory)
    return vectordb



if __name__ == "__main__":
    # measure the time taken to create the vector store
    import time
    start_time = time.time()
    print("Creating vector store from PDF...")
    # Example usage
    input_pdf_path = "FINAL_ELD_TECHNICAL_STANDARD_V1.2_ENGLISH_10-27-2020.pdf"
    vectordb = create_vectordb_from_pdf(input_pdf_path, persist_directory="eld_tech_standard_db")
    print(f"Vector store created in {time.time() - start_time:.2f} seconds.")

    input_pdf_path = "HoS-Application-Guide.pdf"
    vectordb = create_vectordb_from_pdf(input_pdf_path, persist_directory="hos_app_guide_db")
    
    query = "Header Segment"
    query = "What is the purpose of the Header Segment in the ELD Technical Standard?"
    query = "How the Will Pair Sleeper Berth works?"
    start_time = time.time()
    print(f"Querying vector store for: {query}")
    docs = vectordb.similarity_search(query, k=2)
    print(f"Query completed in {time.time() - start_time:.2f} seconds.\n\n")
    
    print("Context retrieved from vector store:")
    for i, doc in enumerate(docs):
        print(f"Chunk {i+1}:\n{doc.page_content}\n")