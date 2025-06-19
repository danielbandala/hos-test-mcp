# Server for retreiving testing suite data and execute tests from any suite
# this mcp is intended to be used with the MCP client (as claude desktop or chatgpt)
# It is a simple example of how to create an MCP server with a tool and a resource

import os
from typing import Any
import json
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from agents.pdf_data_handler_v2 import create_retrieval_data, retrieve_table_data
from agents.report_validator import validate_ccmta_segment
from agents.knowledge_core import retrieve_knowledge

# Load environment variables from .env file
load_dotenv()

# Create an MCP server
mcp = FastMCP(
    name="hos_report_test",
    instructions="This MCP server is designed to handle PDF encoding, chunk retrieval, and CCMTA report validation."
)

#----------------------------------------------------
# Tools and Resources
#----------------------------------------------------

# extract data from a PDF file and create a json file for fast retrieval
# save the file locally and return the path to the file
@mcp.tool(
    name="extract_pdf_data",
    description="Extract data from a PDF file and create a JSON file for future fast retrieval.",
    annotations=ToolAnnotations(
        title="Extract PDF Data",
        readOnlyHint=True,
        description="This tool extracts data from a PDF file and creates a JSON file for future fast retrieval. It saves the file locally and returns the path to the file.",
        parameters={
            "pdf_file_path": {"type": "string", "description": "Path to the PDF file"},
        },
        responses={
            200: {"description": "PDF data extracted and vector database created successfully"},
            400: {"description": "Invalid PDF file path"},
            500: {"description": "Internal server error"}
        },
        required=["pdf_file_path", "vector_db_path"],
        examples=[
            {
                "pdf_file_path": "/path/to/pdf_file.pdf",
                "vector_db_path": "/path/to/vector_db"
            }
        ]
    )
)
def extract_pdf_data(pdf_file_path: str) -> str:
    """Extract data from a PDF file and create a JSON file for future fast retrieval."""
    # verify the PDF file path
    if not pdf_file_path or not isinstance(pdf_file_path, str) or not pdf_file_path.endswith('.pdf'):
        raise ValueError("Invalid PDF file path. Please provide a valid path.")
    
    # Create the vector database from the PDF file
    output_file = create_retrieval_data(pdf_file_path)
    if not output_file:
        raise RuntimeError("Failed to create vector database from the PDF file.")
    
    full_path = os.path.abspath(output_file)
    # Return the path to the output file
    return f"PDF data extracted successfully. Json file created at: {full_path}"




# Tool for retrieving header table data from the JSON file created by extract_pdf_data
@mcp.tool(
    name="get_header_table_data",
    description="Retrieve header table data from a JSON file created by the extract_pdf_data tool.",
    annotations=ToolAnnotations(
        title="Get Header Table Data",
        readOnlyHint=True,
        description="This tool retrieves header table data from a JSON file created by the extract_pdf_data tool.",
        parameters={
            "json_file_path": {"type": "string", "description": "Path to the JSON file created by extract_pdf_data"}
        },
        responses={
            200: {"description": "Header table data retrieved successfully"},
            400: {"description": "Invalid JSON file path"},
            500: {"description": "Internal server error"}
        }
    )
)
def get_header_table_data(json_file_path: str) -> str:
    """Retrieve header table data from a JSON file created by the extract_pdf_data tool."""
    # Verify the JSON file path
    if not json_file_path or not isinstance(json_file_path, str) or not json_file_path.endswith('.json'):
        raise ValueError("Invalid JSON file path. Please provide a valid path.")
    
    # Retrieve the header table data from the JSON file
    table_data = retrieve_table_data(json_file_path, "header")
    if not table_data:
        raise RuntimeError(f"Failed to retrieve table data from {json_file_path}.")
    
    return json.dumps(table_data, indent=4)


# Tool for retrieving Changes in driver's Duty Status, Intermediate Logs and Special Driving Conditions table data from the JSON file
@mcp.tool(
    name="get_duty_status_table_data",
    description="Retrieve the 'Changes in driver's Duty Status, Intermediate Logs and Special Driving Conditions (Personal Use and Yard Moves)' table data from a JSON file created by the extract_pdf_data tool.",
    annotations=ToolAnnotations(
        title="Get Changes in Driver's Duty Status, Intermediate Logs and Special Driving Conditions Table Data",
        readOnlyHint=True,
        description="This tool retrieves the 'Changes in driver's Duty Status, Intermediate Logs and Special Driving Conditions (Personal Use and Yard Moves)' table data from a JSON file created by the extract_pdf_data tool.",
        parameters={
            "json_file_path": {"type": "string", "description": "Path to the JSON file created by extract_pdf_data"}
        },
        responses={
            200: {"description": "Table data retrieved successfully"},
            400: {"description": "Invalid JSON file path"},
            500: {"description": "Internal server error"}
        }
    )
)
def get_duty_status_table_data(json_file_path: str) -> str:
    """Retrieve the 'Changes in driver's Duty Status, Intermediate Logs and Special Driving Conditions (Personal Use and Yard Moves)' table data from a JSON file."""
    if not json_file_path or not isinstance(json_file_path, str) or not json_file_path.endswith('.json'):
        raise ValueError("Invalid JSON file path. Please provide a valid path.")

    table_data = retrieve_table_data(
        json_file_path,
        "changes_in_drivers_duty_status_intermediate_logs_and_special_driving_conditions"
    )
    if not table_data:
        raise RuntimeError(f"Failed to retrieve table data from {json_file_path}.")

    return json.dumps(table_data, indent=4)


@mcp.tool(
    name="get_loginlogout_table_data",
    description="Retrieve the 'Login/Logout, Certification of RODS, Data Diagnostics and Malfunctions' table data from a JSON file created by the extract_pdf_data tool.",
    annotations=ToolAnnotations(
        title="Get Login/Logout, Certification of RODS, Data Diagnostics and Malfunctions Table Data",
        readOnlyHint=True,
        description="This tool retrieves the 'Login/Logout, Certification of RODS, Data Diagnostics and Malfunctions' table data from a JSON file created by the extract_pdf_data tool.",
        parameters={
            "json_file_path": {"type": "string", "description": "Path to the JSON file created by extract_pdf_data"}
        },
        responses={
            200: {"description": "Table data retrieved successfully"},
            400: {"description": "Invalid JSON file path"},
            500: {"description": "Internal server error"}
        }
    )
)
def get_loginlogout_table_data(json_file_path: str) -> str:
    """Retrieve the 'Login/Logout, Certification of RODS, Data Diagnostics and Malfunctions' table data from a JSON file."""
    if not json_file_path or not isinstance(json_file_path, str) or not json_file_path.endswith('.json'):
        raise ValueError("Invalid JSON file path. Please provide a valid path.")

    table_data = retrieve_table_data(
        json_file_path,
        "loginlogout_certification_of_rods_data_diagnostics_and_malfunctions"
    )
    if not table_data:
        raise RuntimeError(f"Failed to retrieve table data from {json_file_path}.")

    return json.dumps(table_data, indent=4)







@mcp.tool(
    name="get_cycle_change_table_data",
    description="Retrieve the 'Change in Driver's Cycle, Change in Operating Zone, Off-duty Time Deferral' table data from a JSON file created by the extract_pdf_data tool.",
    annotations=ToolAnnotations(
        title="Get Change in Driver's Cycle, Change in Operating Zone, Off-duty Time Deferral Table Data",
        readOnlyHint=True,
        description="This tool retrieves the 'Change in Driver's Cycle, Change in Operating Zone, Off-duty Time Deferral' table data from a JSON file created by the extract_pdf_data tool.",
        parameters={
            "json_file_path": {"type": "string", "description": "Path to the JSON file created by extract_pdf_data"}
        },
        responses={
            200: {"description": "Table data retrieved successfully"},
            400: {"description": "Invalid JSON file path"},
            500: {"description": "Internal server error"}
        }
    )
)
def get_cycle_change_table_data(json_file_path: str) -> str:
    """Retrieve the 'Change in Driver's Cycle, Change in Operating Zone, Off-duty Time Deferral' table data from a JSON file."""
    if not json_file_path or not isinstance(json_file_path, str) or not json_file_path.endswith('.json'):
        raise ValueError("Invalid JSON file path. Please provide a valid path.")

    table_data = retrieve_table_data(
        json_file_path,
        "change_in_drivers_cycle_change_in_operating_zone_offduty_time_deferral"
    )
    if not table_data:
        raise RuntimeError(f"Failed to retrieve table data from {json_file_path}.")

    return json.dumps(table_data, indent=4)




@mcp.tool(
    name="get_comments_table_data",
    description="Retrieve the 'Comments, Remarks and Annotations' table data from a JSON file created by the extract_pdf_data tool.",
    annotations=ToolAnnotations(
        title="Get Comments, Remarks and Annotations Table Data",
        readOnlyHint=True,
        description="This tool retrieves the 'Comments, Remarks and Annotations' table data from a JSON file created by the extract_pdf_data tool.",
        parameters={
            "json_file_path": {"type": "string", "description": "Path to the JSON file created by extract_pdf_data"}
        },
        responses={
            200: {"description": "Table data retrieved successfully"},
            400: {"description": "Invalid JSON file path"},
            500: {"description": "Internal server error"}
        }
    )
)
def get_comments_table_data(json_file_path: str) -> str:
    """Retrieve the 'Comments, Remarks and Annotations' table data from a JSON file."""
    if not json_file_path or not isinstance(json_file_path, str) or not json_file_path.endswith('.json'):
        raise ValueError("Invalid JSON file path. Please provide a valid path.")

    table_data = retrieve_table_data(
        json_file_path,
        "comments_remarks_and_annotations"
    )
    if not table_data:
        raise RuntimeError(f"Failed to retrieve table data from {json_file_path}.")

    return json.dumps(table_data, indent=4)





@mcp.tool(
    name="get_additional_hours_table_data",
    description="Retrieve the 'Additional Hours Not Recorded' table data from a JSON file created by the extract_pdf_data tool.",
    annotations=ToolAnnotations(
        title="Get Additional Hours Not Recorded Table Data",
        readOnlyHint=True,
        description="This tool retrieves the 'Additional Hours Not Recorded' table data from a JSON file created by the extract_pdf_data tool.",
        parameters={
            "json_file_path": {"type": "string", "description": "Path to the JSON file created by extract_pdf_data"}
        },
        responses={
            200: {"description": "Table data retrieved successfully"},
            400: {"description": "Invalid JSON file path"},
            500: {"description": "Internal server error"}
        }
    )
)
def get_additional_hours_table_data(json_file_path: str) -> str:
    """Retrieve the 'Additional Hours Not Recorded' table data from a JSON file."""
    if not json_file_path or not isinstance(json_file_path, str) or not json_file_path.endswith('.json'):
        raise ValueError("Invalid JSON file path. Please provide a valid path.")

    table_data = retrieve_table_data(
        json_file_path,
        "additional_hours_not_recorded"
    )
    if not table_data:
        raise RuntimeError(f"Failed to retrieve table data from {json_file_path}.")

    return json.dumps(table_data, indent=4)





@mcp.tool(
    name="get_engine_table_data",
    description="Retrieve the 'Engine Power Up and Shut Down' table data from a JSON file created by the extract_pdf_data tool.",
    annotations=ToolAnnotations(
        title="Get Engine Power Up and Shut Down Table Data",
        readOnlyHint=True,
        description="This tool retrieves the 'Engine Power Up and Shut Down' table data from a JSON file created by the extract_pdf_data tool.",
        parameters={
            "json_file_path": {"type": "string", "description": "Path to the JSON file created by extract_pdf_data"}
        },
        responses={
            200: {"description": "Table data retrieved successfully"},
            400: {"description": "Invalid JSON file path"},
            500: {"description": "Internal server error"}
        }
    )
)
def get_engine_table_data(json_file_path: str) -> str:
    """Retrieve the 'Engine Power Up and Shut Down' table data from a JSON file."""
    if not json_file_path or not isinstance(json_file_path, str) or not json_file_path.endswith('.json'):
        raise ValueError("Invalid JSON file path. Please provide a valid path.")

    table_data = retrieve_table_data(
        json_file_path,
        "engine_power_up_and_shut_down"
    )
    if not table_data:
        raise RuntimeError(f"Failed to retrieve table data from {json_file_path}.")

    return json.dumps(table_data, indent=4)




# Tool for validating CCMTA reports
@mcp.tool(
    name="validate_report_chunk",
    description="Validate a CCMTA report against HoS regulations and ELD technical standards.",
    annotations=ToolAnnotations(
        title="Validate CCMTA Report",
        readOnlyHint=True,
        description="This tool validates a CCMTA report segment against the schema defined by the CCMTA ELD technical standards and HoS regulations.",
        parameters={
            "report_chunk": {"type": "string", "description": "CCMTA report segment to validate"},
            "eld_tech_knowledge": {"type": "string", "description": "Knowledge about ELD technical standards"},
            "hos_reg_knowledge": {"type": "string", "description": "Knowledge about HoS regulations"}
        },
        responses={
            200: {"description": "CCMTA report validated successfully"},
            400: {"description": "Invalid report format"},
            500: {"description": "Internal server error"}
        }
    )
)
def validate_report_chunk(report_chunk: str, eld_tech_knowledge: str, hos_reg_knowledge) -> str:
    """Validate a CCMTA report against the schema"""    
    # Validate the CCMTA report
    validation_result = validate_ccmta_segment(report_chunk, eld_tech_knowledge, hos_reg_knowledge)
    if not validation_result:
        raise RuntimeError("CCMTA report validation failed.")
    
    return f"CCMTA report validated successfully: {validation_result}"


@mcp.tool(
    name="retrieve_ccmta_eld_knowledge",
    description="Retrieve knowledge about CCMTA ELD (Electronic Logging Device) requirements and technical standards.",
    annotations=ToolAnnotations(
        title="Retrieve CCMTA ELD Knowledge",
        readOnlyHint=True,
        description="This tool retrieves knowledge about CCMTA ELD (Electronic Logging Device) requirements and technical standards.",
        parameters={
            "query": {"type": "string", "description": "Query to search for specific CCMTA ELD knowledge"}
        },
        responses={
            200: {"description": "Knowledge retrieved successfully"},
            404: {"description": "Knowledge not found"},
            500: {"description": "Internal server error"}
        }
    )
)
def retrieve_ccmta_eld_knowledge(query: str) -> str:
    """Retrieve knowledge about CCMTA ELD (Electronic Logging Device) requirements and technical standards."""
    if not query or not isinstance(query, str):
        raise ValueError("Invalid query. Please provide a valid query string.")
    
    # Retrieve knowledge from the knowledge core
    knowledge = retrieve_knowledge(vector_db_path="./agents/eld_tech_standard_db" , query=query)
    if not knowledge:
        raise RuntimeError("Failed to retrieve CCMTA ELD knowledge.")
    
    knowledge_str = "\n".join(chunk.page_content for chunk in knowledge)
    return f"CCMTA ELD Knowledge: {knowledge_str}"


@mcp.tool(
    name="retrieve_ccmta_hos_regulations_knowledge",
    description="Retrieve knowledge about the application guide of CCMTA HoS (Hours of Service) regulations.",
    annotations=ToolAnnotations(
        title="Retrieve CCMTA HoS Regulations Knowledge",
        readOnlyHint=True,
        description="This tool retrieves knowledge about the application guide of CCMTA HoS (Hours of Service) regulations.",
        parameters={
            "query": {"type": "string", "description": "Query to search for specific CCMTA HoS regulations knowledge"}
        },
        responses={
            200: {"description": "Knowledge retrieved successfully"},
            404: {"description": "Knowledge not found"},
            500: {"description": "Internal server error"}
        }
    )
)
def retrieve_ccmta_hos_regulations_knowledge(query: str) -> str:
    """Retrieve knowledge about the application guide of CCMTA HoS (Hours of Service) regulations."""
    if not query or not isinstance(query, str):
        raise ValueError("Invalid query. Please provide a valid query string.")
    
    # Retrieve knowledge from the knowledge core
    knowledge = retrieve_knowledge(vector_db_path="./agents/hos_app_guide_db", query=query)
    if not knowledge:
        raise RuntimeError("Failed to retrieve CCMTA HoS regulations knowledge.")
    
    knowledge_str = "\n".join(chunk.page_content for chunk in knowledge)
    return f"CCMTA HoS Regulations Knowledge: {knowledge_str}"


