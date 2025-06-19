## this is goind to be a pdf validator agent
from dotenv import load_dotenv
import os
import base64
import json

from openai import OpenAI

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Ensure the .env file is loaded to access environment variables
load_dotenv()

input_pdf_path = "US2__6028061125-121602771.pdf"

llm_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


loader = PyPDFLoader(input_pdf_path, mode="single")
docs = loader.load()  # list of Document objects
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
chunks = splitter.split_documents(docs)


# Create embeddings and vector store
embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model="text-embedding-3-small"
)
vectordb = Chroma.from_documents(chunks, embeddings, persist_directory="db")

# save the vector store to disk
# vectordb.persist()

# Retrieve relevant chunks based on a query
query = "PDF title and section list"

query = "Login/Logout, Certification of RODS, Data Diagnostics and Malfunctions"
docs = vectordb.similarity_search(query, k=5)
context = "\n\n".join(d.page_content for d in docs)


# Print the context retrieved from the vector store
print("Context retrieved from vector store:")
for i, doc in enumerate(docs):
    print(f"Chunk {i+1}:\n{doc.page_content}\n")

print("\n\n")

# prompt = f"""
# Validate this JSON: must have keys "title", "sections" (list of strings).
# Only use what's in context:
# {context}

# Return ONLY valid JSON or an error JSON.
# Avoid repetition, be concise.
# """

messages = [
    {"role": "system", "content": "You are a CCMTA (Canadian Council of Motor Transport Administrators) report validator that takes a text input from a pdf report chunk, structures the data and validates what the user asks."},
    {"role": "user", "content": (
        "Report chunk:\n\n" + context + "\n\n"
        "Validate if the information is structured correctly, the parameters are in the right format, and the data is complete.\n"+
        "Validate the table data against what is expected for that segment in the CCMTA report. Use most updated information\n"
    )}
]

resp = llm_client.chat.completions.create(
    model="gpt-4o-mini-search-preview",
    messages=messages,
    max_tokens=300,
    web_search_options={
        "search_context_size": "low",
    },

)
print(resp.choices[0].message.content)






# # JSON schema for validation: check PDF has title and sections list
# MY_SCHEMA = {
#   "type": "object",
#   "properties": {
#     "title": {"type": "string"},
#     "sections": {
#       "type": "array",
#       "items": {"type": "string"},
#       "minItems": 1
#     }
#   },
#   "required": ["title", "sections"],
#   "additionalProperties": False
# }

# def validate_pdf(path):
#     pdf_b64 = base64.b64encode(open(path, "rb").read()).decode()
#     resp = llm_client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are a PDF validator."},
#             {"role": "user", "content": (
#                 "Validate this PDF returns JSON matching this schema:\n"
#                 + json.dumps(MY_SCHEMA) + "\n"
#                 "Return only the JSON, nothing else."
#             )},
#             {"role": "user", "name": "pdf", "content": pdf_b64}
#         ]
#     )
#     out = resp.choices[0].message.content
#     try:
#         data = json.loads(out)
#         print("✅ ✅ PDF is valid:", data)
#     except json.JSONDecodeError:
#         print("❌ Invalid JSON response:", out)






