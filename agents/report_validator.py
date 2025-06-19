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

llm_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

def validate_ccmta_segment(report_chunk: str, eld_tech_knowledge: str, hos_reg_knowledge) -> str:
    """
    Validate the CCMTA report chunk and return structured data or error message.
    
    Args:
        report_chunk (str): The text content of the CCMTA report chunk.
        eld_tech_knowledge (str): Knowledge about ELD technology.
        hos_reg_knowledge (str): Knowledge about HOS regulations.
        
    Returns:
        str: Validated JSON or error message.
    """
    messages = [
        {"role": "system", "content": "You are a CCMTA (Canadian Council of Motor Transport Administrators) report validator. You are an expert in validating and structuring CCMTA report data according to federal compliance requirements."},
        {"role": "user", "content": (
            "Report chunk:\n\n" + report_chunk + "\n\n"
            "Validate if the information is structured correctly, the parameters are in the right format, and the data is complete.\n"
            "Validate if the report segment data includes all requirements from CCMTA federal compliance. Specify any missing or incorrect data.\n"
            "Here is the knowledge you should use for validation:\n"
            "ELD Technical Knowledge: " + eld_tech_knowledge + "\n"
            "HOS Regulations Knowledge: " + hos_reg_knowledge + "\n\n"
            "If the report segment is valid, return a JSON object with the following structure:\n"
            "{\n"
            "  'valid': true,\n"
            "  'data': {\n"
            "    'segment_id': 'string',\n"
            "    'timestamp': 'YYYY-MM-DDTHH:MM:SSZ',\n"
            "    'driver_id': 'string',\n"
            "    'vehicle_id': 'string',\n"
            "    'location': {\n"
            "      'latitude': float,\n"
            "      'longitude': float\n"
            "    },\n"
            "    'event_type': 'string',\n"
            "    'event_description': 'string',\n"
            "    'eld_tech_knowledge': '" + eld_tech_knowledge + "',\n"
            "    'hos_reg_knowledge': '" + hos_reg_knowledge + "'\n"
            "  }\n"
        )}
    ]
    
    response = llm_client.chat.completions.create(
        model="gpt-4o-mini-search-preview",
        messages=messages,
        max_tokens=1024,
        web_search_options={
            "search_context_size": "low",
        },
    )
    
    return response.choices[0].message.content
