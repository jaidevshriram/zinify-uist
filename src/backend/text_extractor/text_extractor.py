import PyPDF2

from threading import Lock

lock = Lock()

# Your existing function to extract PDF content
def extract_pdf_content_bytesio(pdf_path):
    text = ""
    reader = PyPDF2.PdfReader(pdf_path)
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()
    return text

def extract_pdf_content(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text


import requests
from xml.etree import ElementTree
from io import BytesIO


def get_arxiv_paper(arxiv_id):
    base_url = "http://export.arxiv.org/api/query?id_list="
    url = f"{base_url}{arxiv_id}"

    response = requests.get(url)
    if response.status_code == 200:
        tree = ElementTree.fromstring(response.content)
        for entry in tree.findall(".//{http://www.w3.org/2005/Atom}entry"):
            pdf_url = entry.find(
                "{http://www.w3.org/2005/Atom}link[@title='pdf']"
            ).attrib["href"]

            # Download the PDF into memory
            pdf_response = requests.get(f"{pdf_url}.pdf")
            if pdf_response.status_code == 200:
                pdf_path = BytesIO(pdf_response.content)
                return pdf_path
    return None


import re
import os


def extract_text_from_any(input_str):
    # Check if the input is a local PDF path
    if input_str.lower().endswith(".pdf"):
        if os.path.exists(input_str):
            with open(input_str, "rb") as file:
                return True, extract_pdf_content_bytesio(file)

    # Check if the input matches the arXiv URL format

    # if starts with http:// or https://, remove it
    if input_str.startswith("http://") or input_str.startswith("https://"):
        input_str = input_str.split("://")[1]

    arxiv_url_match = re.search(r"arxiv\.org/abs/(\d+\.\d+)", input_str)
    if arxiv_url_match:
        arxiv_id = arxiv_url_match.group(1)
        pdf_path = get_arxiv_paper(arxiv_id)
        print(pdf_path, " is arxiv pdf path")
        if pdf_path:
            return True, extract_pdf_content_bytesio(pdf_path)

    # If neither of the above checks pass, treat the input as an arXiv ID
    else:
        pdf_path = get_arxiv_paper(input_str)
        if pdf_path:
            return True, extract_pdf_content(pdf_path)

    return False, "Invalid input or could not fetch the paper."


# Rest of your code remains unchanged.

def extract_text(cfg, content, verbose=False, max_chars=80000, write_to_file=True):

    status, pdf_text = extract_text_from_any(cfg["pdf_path"])

    if not status:
        if verbose:
            print("PDF extraction failed")
            print(pdf_text)

        return False
    

    if verbose:
        if len(pdf_text) > max_chars:
            print("PDF too long, truncating to first 80000 characters")

    pdf_text = pdf_text[:max_chars]

    sample = (
        pdf_text[:100] + " ... " + pdf_text[-100:] if len(pdf_text) > 200 else pdf_text
    )
    # remove newlines
    sample = sample.replace("\n", " ")

    if verbose:
        print("PDF extracted successfully")
        print("PDF text length: ", len(pdf_text))

        print(sample)
        print("\n\n")

    with lock:
        content["pdf_text"] = pdf_text

    with lock:
        content["sample"] = sample

    #cfg["pdf_text"] = pdf_text
    #cfg["sample"] = sample

    return True
