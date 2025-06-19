## this is goind to be a pdf validator agent
import os
import json
import time
import pdfplumber
import re

def extract_tables_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        str: Extracted text from the PDF.
    """
    logs_date = "2023-10-01"  # Default value for logs_date
    pdf_tables = {}
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        current_page = 0
        for page in pdf.pages:
            current_page += 1
            print(f"Processing page {current_page} of {total_pages}...")
            # Extract text from pdf page
            txt = page.extract_text().lower() if page.extract_text() else ""
            # extract tables from pdf page
            tables = page.extract_tables()
            for tbl in tables:
                if not tbl:
                    continue
                try:
                    # Store the table in the dictionary with the logs_date as the primary key and report title as the secondary key
                    table_id = tbl[0][0].lower().strip() if tbl[0][0] is not None else None  # Assuming the first cell is the table ID
                    # if the first cell is empty, this means the table is continuation of the previous page
                    if table_id is not None:
                        if "date of rods" in table_id:
                            # table is header segment
                            table_title = "header"
                            # If the table ID is "date of rods", use the second cell as the logs_date
                            logs_date = tbl[1][0]
                            data_table = tbl 
                        else:
                            table_title = table_id if table_id and len(table_id)>0 else table_title
                            data_table = tbl[1:][:]  # Skip the first row which is the header
                            # remove special characters from the table title and put all words together
                            words = table_title.replace(" ", "_").lower().split("_")
                            table_title = "_".join(words[:11])
                            table_title = re.sub('[^a-z0-9_]+', '', table_title)

                    if "unidentified driver profile" in txt:
                        logs_date = "unidentified_driver"

                    if logs_date not in pdf_tables:
                        pdf_tables[logs_date] = {}
                    if table_title not in pdf_tables[logs_date]:
                        pdf_tables[logs_date][table_title] = []
                    # add data only if two or more columns contain data
                    for row in data_table:
                        if all(cell is None or cell.strip() == "" for cell in row):
                            data_table.remove(row)
                    pdf_tables[logs_date][table_title].append(data_table)
                except Exception as e:
                    print(f"Error extracting table on page {page.page_number}: {e}")
                    print(f"Table content: {tbl}")
                    continue
    return pdf_tables


def create_retrieval_data(pdf_path: str, output_file: str="pdf_tables.json") -> None:
    """
    Extract tables from a PDF file and save them to a JSON file.
    Args:
        pdf_path (str): Path to the PDF file.
        output_file (str): Path to the output JSON file.
    """
    tables = extract_tables_from_pdf(pdf_path)

    # output file will be in the same directory as the PDF file
    output_file = os.path.splitext(pdf_path)[0] + "_tables.json"
    
    # Save the extracted tables to a JSON file
    with open(output_file, "w") as f:
        json.dump(tables, f, indent=4)
    
    return output_file #if os.path.exists(output_file) else None





def retrieve_table_data(data_file_path: str, table_id: str) -> list[str]:
    """
    Retrieve table data by table ID.
    Args:
        table_id (str): The ID of the table to retrieve.
    Returns:
        list[str]: List of strings representing the table data.
    """
    # Load the JSON file containing the extracted tables
    with open(data_file_path, "r") as f:
        tables = json.load(f)
    
    # Search for the table ID in the loaded tables
    data = []
    for _, date_tables in tables.items():
        if table_id in date_tables:
            data.append(date_tables[table_id])
    
    return data


if __name__ == "__main__":
    # Example usage
    start_time = time.time()
    pdf_path = "US2__6028061125-121602771.pdf"  # Replace with your PDF file path
    output_json = create_retrieval_data(pdf_path)
    print(f"Extracted tables saved to {output_json} in {time.time() - start_time:.4f} seconds.")
    # Create a vector database from the PDF
    start_time = time.time()
    data = retrieve_table_data(output_json, "header")
    elapsed_time = time.time() - start_time
    print(f"Retrieval took {elapsed_time:.4f} seconds.")