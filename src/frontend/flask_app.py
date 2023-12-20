from flask import Flask, render_template, request, redirect, url_for, jsonify

import time, threading, random

import os

from typing import Dict

#from backend.layout_generator import generate_layout
#from image_generator import generate_images
from backend.content_generator import generate_content_threadable
#from zine_assembler import assemble_zine

app = Flask(__name__)

zine_plan_done = False

# Create a lock
lock = threading.Lock()

zine_plan_data_default = {
    "summary": "Reading your paper...",
    "box1": "Planning Page 1...",
    "box2": "Planning Page 2...",
    "box3": "Planning Page 3...",
    "box4": "Planning Page 4...",
    "box5": "Planning Page 5...",
    "box6": "Planning Page 6...",
}

zine_selection = {}

def format_content_summary(summary):
    _, summary_text, plan_text = summary.split("Human:")
    summary_text = summary_text.strip().split("Assistant:")[1].strip()
    plan_text = plan_text.strip().split("Assistant:")[1].strip()

    summary_content = ""
    summary_content += "Summary Generated successfully!\nSummary: " + summary_text + "\n\n"
    summary_content += "Zine Plan Generated successfully!\nZine Plan: " + plan_text + "\n\n"

def format_content_page(page):
    """   page =  {
        "image_description": image_descriptions,
        "image_phrases": image_phrases,
        #"short_texts": short_texts,
        #"long_texts": long_texts,
        "heading": heading_texts,
        "body_texts": body_texts,
        "title": title_texts,
        "abstract": abstract_texts,
        "catchy_text": catchy_texts,
    }
    All are lists, if list is empty don't add to text
    """

    output = ""
    for key in page:
        if page[key] != []:
            output += key.upper() + ":\n"
            for text in page[key]:
                output += text + "\n"
            output += "\n"
    
    return output

    


@app.route("/", methods=["GET", "POST"])
def index():
    global zine_plan_done
    zine_plan_done = False  # Reset the flag

    global zine_plan_data
    zine_plan_data = zine_plan_data_default

    global zine_selection

    if request.method == "POST":
        # Here you can process the data sent from the form
        style = request.form.get("style")
        option = request.form.get("option")
        link = request.form.get("link")

        zine_selection = {
            "image_generator": {
                "type": "stable_diffusion_xl",  # dalle3, sd2, sd1, sdxl
            },
            "content_type": "primer",  # introduction, informative, highlight
            "style": "fantasy",  # sci fi, fantasy, or freeform (input field)
            "project_name": "trial",
            "pdf_path": "./sample_pdfs/2308.12950.pdf",
            "page_count": 6,
        }

        # After processing, redirect to the loading page
        return redirect(url_for("loading"))

    return render_template("landing_page.html")


def random_content():
    """Generate a random string for demonstration."""
    return "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(5))

def extract_content(zine_content, display_content):
    if "sample" in zine_content:
        display_content["summary"] = "Paper Extracted successfully!\nSample: " + zine_content["sample"] + "\n\n"
    if "summary" in zine_content:
        summary = zine_content["summary"]
        display_content["summary"] += format_content_summary(summary)
    
    for i, page in enumerate(zine_content["page_contents"]):
        if page is not None:
            display_content["box" + str(i+1)] = format_content_page(page)
    



def backend_generation():
    global zine_plan_done, zine_plan_data, zine_selection

    layout_cfg =  {
    "layout_type": "z_layout",  # or 'open_book'
    "pages": [
        {
            "html_layout": "path_to_layout.html",
            "requirements": {
                "title": 1,
                "abstract": 0,
                "heading": 0,
                "catchy_text": 0,
                "num_images": 1,
                "text_boxes": 0,
                "word_count": [30, 5],
            },
        },
        {
            "html_layout": "path_to_layout.html",
            "requirements": {
                "title": 0,
                "abstract": 0,
                "heading": 1,
                "catchy_text": 0,
                "num_images": 1,
                "text_boxes": 1,
                "word_count": [30, 5],
            },
        },
        {
            "html_layout": "path_to_layout.html",
            "requirements": {
                "title": 0,
                "abstract": 0,
                "heading": 1,
                "catchy_text": 0,
                "num_images": 1,
                "text_boxes": 1,
                "word_count": [30, 5],
            },
        },
                {
            "html_layout": "path_to_layout.html",
            "requirements": {
                "title": 0,
                "abstract": 0,
                "heading": 0,
                "catchy_text": 1,
                "num_images": 1,
                "text_boxes": 0,
                "word_count": [30, 5],
            },
        },
                {
            "html_layout": "path_to_layout.html",
            "requirements": {
                "title": 0,
                "abstract": 0,
                "heading": 1,
                "catchy_text": 0,
                "num_images": 1,
                "text_boxes": 1,
                "word_count": [30, 5],
            },
        },
                {
            "html_layout": "path_to_layout.html",
            "requirements": {
                "title": 0,
                "abstract": 1,
                "heading": 1,
                "catchy_text": 0,
                "num_images": 1,
                "text_boxes": 0,
                "word_count": [30, 5],
            },
        },
    ],
    }

    content = {}

    # start a thread to generate the content

    content_thread = threading.Thread(target=generate_content_threadable, args=(zine_selection, layout_cfg, content))
    content_thread.start()

    while content_thread.is_alive():
        # update zine_plan_data

        extract_content(content, zine_plan_data)

        time.sleep(0.1)
    
    # done

    # update zine_plan_done
    with lock:
        zine_plan_done = True



@app.route("/loading")
def loading():
    global zine_plan_done

    # Check if the thread is already running
    if not zine_plan_done:
        threading.Thread(target=backend_generation).start()
        return render_template("loading_page.html")
    else:
        return "A thread is already running.", 429  # HTTP status code for 'Too Many Requests'


@app.route("/is_done")
def is_done():
    global zine_plan_done
    if zine_plan_done:
        return {"done": True}
    else:
        return {"done": False}


@app.route("/data")
def data():
    global zine_plan_data
    return jsonify(zine_plan_data)


@app.route("/finished")
def finished():
    return render_template("zine.html")


if __name__ == "__main__":
    app.run(debug=True)
