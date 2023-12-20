import os
from werkzeug.utils import secure_filename

import os
import json
from typing import Dict

from selenium import webdriver

import pdfkit


import asyncio
from pyppeteer import launch

import os
import subprocess

import qrcode
import PyPDF2
from PyPDF2 import PdfFileReader, PdfFileWriter
from PIL import Image

zine_plan_data_default = {
    "summary": "Reading your paper...",
    "box1": "Planning Page 1...",
    "box2": "Planning Page 2...",
    "box3": "Planning Page 3...",
    "box4": "Planning Page 4...",
    "box5": "Planning Page 5...",
    "box6": "Planning Page 6...",
}
zine_plan_data = dict(zine_plan_data_default)

UPLOAD_FOLDER = "uploads"
def process_form_to_cfg(form, request):
    style = form.get("style")
    option = form.get("option")
    email = form.get("email")

    print(request.form)

    # Check if there's an uploaded file and it's named 'pdf' in the form
    if 'pdf' in request.files and request.files['pdf'].filename != '':
        file = request.files['pdf']

        # Check if the file isn't empty
        if file.filename != '':
            # Secure the filename and save it
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Use the filepath instead of the link
            link = filepath
        else:
            print("issue?")
    else:
        link = request.form.get("link")
    
    return {
        "image_generator": {
            "type": "stable_diffusion_xl",  # dalle3, sd2, sd1, sdxl
        },
        "content_type": option,  # introduction, informative, highlight
        "email": email,
        "style": style,  # sci fi, fantasy, or freeform (input field)
        "pdf_path": link,
        "project_id": os.urandom(16).hex(),
        "page_count": 6,
    }


def format_content_summary(summary):
    _, summary_text, plan_text = summary.split("Human:")
    summary_text = summary_text.strip().split("Assistant:")[1].strip()
    plan_text = plan_text.strip().split("Assistant:")[1].strip()

    summary_content = ""
    summary_content += "Summary Generated successfully!\n"  # + summary_text[:40].strip() + "..." + "<br>"
    summary_content += "Zine Plan Generated successfully!\n"  # + plan_text[:20].strip() + "..." + "<br>"

    return summary_content


def format_content_page(page):
    output = ""
    for key in page:
        if key.strip() != "image_description" and key.strip() != "body_texts":
            continue

        # print(key)
        if page[key] != []:
            for text in page[key]:
                output += text[:150].strip() + "..." + "\n"
            output += "\n"

    return output


def extract_content(zine_content, display_content):
    if zine_content is None:
        return
    if "summary" in zine_content and zine_content["summary"] is not None:
        # summary = zine_content["summary"]
        # display_content["summary"] = format_content_summary(summary)
        display_content["summary"] = "Zine Plan Generated successfully!"
    if "page_contents" in zine_content and zine_content["page_contents"] is not None:
        for i, page in enumerate(zine_content["page_contents"]):
            if page is not None:
                display_content["box" + str(i + 1)] = format_content_page(page)
                display_content["summary"] += "<br>Planning Page " + str(i + 1) + "..."

def combine_pdfs(pdf1_path, pdf2_path, output_path):
    """
    Combine two PDF files into one output PDF.

    Args:
    - pdf1_path (str): Path to the first PDF.
    - pdf2_path (str): Path to the second PDF.
    - output_path (str): Path to save the combined PDF.
    """
    # Create PDF reader objects
    pdf1 = open(pdf1_path, 'rb')
    pdf2 = open(pdf2_path, 'rb')
    reader1 = PyPDF2.PdfFileReader(pdf1)
    reader2 = PyPDF2.PdfFileReader(pdf2)

    # Create a PDF writer object
    writer = PyPDF2.PdfFileWriter()

    # Append pages from the first PDF
    for page_num in range(reader1.numPages):
        page = reader1.getPage(page_num)
        writer.addPage(page)

    # Append pages from the second PDF
    for page_num in range(reader2.numPages):
        page = reader2.getPage(page_num)
        writer.addPage(page)

    # Write the combined PDF to the output file
    with open(output_path, 'wb') as output_pdf:
        writer.write(output_pdf)

    # Close the PDF files
    pdf1.close()
    pdf2.close()

def generate_qr_code(data, save_path="qr.png"):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    img = img.resize((200, 200))
    img.save(save_path)
    return img

def overlay_qr_on_pdf(pdf_path, qr_img, x, y, output_path="output.pdf"):
    # Load the PDF
    with open(pdf_path, "rb") as pdf_file:
        reader = PdfFileReader(pdf_file)
        writer = PdfFileWriter()
        page = reader.getPage(0)
        
        # Convert QR code image to PDF
        qr_pdf_path = "qr_tmp.pdf"
        qr_img.save(qr_pdf_path, "PDF", resolution=100.0)
        
        with open(qr_pdf_path, "rb") as qr_pdf_file:
            qr_pdf = PdfFileReader(qr_pdf_file)
            # Overlay the QR code onto the PDF page
            page.mergeTranslatedPage(qr_pdf.getPage(0), x, y)
            writer.addPage(page)
            
            # Save the output PDF
            with open(output_path, "wb") as output_pdf_file:
                writer.write(output_pdf_file)

def export_html_to_png(input_html, output_png, url=False):

    from html2image import Html2Image
    # hti = Html2Image(size=(1414, 1000))
    hti = Html2Image(size=(1414, 1000))
    
    output_png_snip = os.path.basename(output_png)

    if not url:
        hti.screenshot(
            html_file=input_html,
            # save_as=f"{input_html.replace('html', 'png')}"
            save_as=output_png_snip
        )
    else:
        hti.screenshot(
            url=input_html,
            # save_as=f"{input_html.replace('html', 'png')}"
            save_as=output_png_snip
        )

    # Move the output to the correct location
    os.rename(output_png_snip, output_png)
