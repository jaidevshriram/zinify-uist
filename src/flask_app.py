# Flask imports
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash

# Standard library imports
import os
import time
import threading
import random
from typing import Dict

# Local module imports
from backend.layout_generator import generate_layout
from backend.content_generator import generate_content_threadable
from backend.image_generator_stability import generate_images_stability
from backend.text_extractor import extract_text
from backend.zine_assembler import assemble_zine
from webapp_helpers import *


app = Flask(__name__, static_url_path="/static")

zine_done = False
session_dict = {}

lock = threading.Lock()


@app.route("/", methods=["GET", "POST"])
def index():
    global zine_done
    zine_done = False  # Reset the flag

    global zine_plan_data
    zine_plan_data = dict(zine_plan_data_default)

    global zine_selection

    global session_dict

    if request.method == "POST":
        zine_cfg = process_form_to_cfg(request.form, request)
        layout_cfg = generate_layout(zine_cfg)
        content = {}
        status = extract_text(zine_cfg, content=content)

        if status == "error":
            # Use flash to send a message to the next page
            flash("Invalid input!")
            return redirect(url_for("index"))  # Redirect back to the same page

            # Save the configurations to the session

        session_dict["zine_cfg"] = zine_cfg
        session_dict["layout_cfg"] = layout_cfg
        session_dict["content"] = content

        return redirect(url_for("loading"))

    return render_template("landing_page.html")


def backend_generation(zine_cfg, layout_cfg, content):
    global zine_done, zine_plan_data, zine_selection

    content_thread = threading.Thread(
        target=generate_content_threadable, args=(zine_cfg, layout_cfg, content)
    )
    content_thread.start()

    while content_thread.is_alive():
        extract_content(content, zine_plan_data)
        time.sleep(0.1)

    # zine_plan_data["summary"] = "\n"
    with lock:
        zine_plan_data["summary"] = "Please wait while we generate the images..."

    image_outputs = generate_images_stability(zine_cfg, content)

    with lock:
        zine_plan_data["summary"] = "Almost there! Putting your zine together..."

    zine_sheets = assemble_zine(
        zine_cfg, layout_cfg, content, image_outputs, use_abs_path=False
    )
    web_zine_sheets = zine_sheets["web_sheet"]
    zine_sheets = zine_sheets["sheet"]

    # Copy the static folder
    os.makedirs("templates/static", exist_ok=True)
    subprocess.run("cp -r //Users/jaidev/Desktop/ZINify/static/ /Users/jaidev/Desktop/ZINify/templates/static", shell=True)

    # Write regular sheets to html file
    for i, sheet in enumerate(web_zine_sheets):
        with open(f"templates/zine{i+1}.html", "w") as f:
            f.write(sheet)

    # Write the print sheets to html file
    for i, sheet in enumerate(zine_sheets):
        with open(f"templates/zine{i+1}_print.html", "w") as f:
            f.write(sheet)

    # Write the htmls to a dedicated folder for the zine
    zine_folder = f"webapp_generations/{zine_cfg['project_id']}"
    if not os.path.exists(zine_folder):
        os.makedirs(zine_folder)

    # Export to PNGs
    for i, sheet in enumerate(web_zine_sheets):
        export_html_to_png(
            f"http://localhost:6006/zine{i+1}",
            f"{zine_folder}/zine{i+1}.png",
            url=True
        )

        export_html_to_png(
            f"templates/zine{i+1}_print.html",
            f"{zine_folder}/zine{i+1}_print.png",
            url=False,
        )

    subprocess.run(f"img2pdf {zine_folder}/zine1_print.png {zine_folder}/zine2_print.png -o {zine_folder}/zine_print.pdf", shell=True)
    subprocess.run(f"img2pdf {zine_folder}/zine1.png {zine_folder}/zine2.png -o {zine_folder}/zine.pdf", shell=True)

    with lock:
        zine_done = True

@app.route("/loading")
def loading():
    global zine_done, session_dict

    zine_cfg = session_dict.get("zine_cfg", None)
    layout_cfg = session_dict.get("layout_cfg", None)
    content = session_dict.get("content", None)

    if zine_cfg is None or layout_cfg is None or content is None:
        return redirect(url_for("index"))

    # Check if the thread is already running
    if not zine_done:
        threading.Thread(
            target=backend_generation,
            kwargs={"zine_cfg": zine_cfg, "layout_cfg": layout_cfg, "content": content},
        ).start()
        return render_template("loading_page.html")
    else:
        return (
            "A thread is already running.",
            429,
        )  # HTTP status code for 'Too Many Requests'


@app.route("/is_done")
def is_done():
    global zine_done
    if zine_done:
        return {"done": True}
    else:
        return {"done": False}


@app.route("/data")
def data():
    global zine_plan_data
    return jsonify(zine_plan_data)


@app.route("/finished")
def finished():
    if not zine_done:
        return redirect(url_for("loading"))
    else:
        return redirect(url_for("zine1"))

    return render_template("zine.html")


@app.route("/zine1")
def zine1():
    # if not zine_done:
    #    return redirect(url_for("loading"))

    return render_template("zine1.html")


@app.route("/zine2")
def zine2():
    # if not zine_done:
    #    return redirect(url_for("loading"))

    return render_template("zine2.html")

if __name__ == "__main__":
    app.run(debug=True, port=6006)