import multiprocessing
from threading import Lock
import os
import json

lock = Lock()

#from text_extractor import extract_text
from .prompt_templates import *
from .llm_conversation.claude_conversation import ClaudeConversation


def summarize_zine(cfg, verbose=False):
    conv = ClaudeConversation()
    out = conv.add_message(human_message=summarize_template, context=cfg["pdf_text"])
    if verbose:
        print(out)
    plan_template = get_zine_plan_template(
        cfg["page_count"], cfg["style"], cfg["content_type"]
    )
    out = conv.add_message(human_message=plan_template)
    if verbose:
        print(out)
    conv.scrub_context()
    return conv.conversation


def plan_single_page(page_number, page_cfg, conversation, page_contents):
    print(
        "Function plan_single_page is deprecated. Use plan_single_page_threadable instead."
    )
    raise NotImplementedError
    """
    page_number: page number to plan (0 indexed)
    image_count: number of images on the page

    sample page_cfg:

    {
        'title': 0,
        'abstract': 0,
        'heading': 0,
        'catchy_text': 0,
        'num_images': 1,
        'text_boxes': 2,
        'word_count': [30, 5]
    }

    """

    conv = ClaudeConversation()
    conv.conversation = conversation
    page_template = get_page_template(page_number, page_cfg)
    page_plan_text = conv.add_message(human_message=page_template, asst_message="<")
    page_contents[page_number] = extract_page_reply(page_plan_text)

    return page_contents


def plan_pages(cfg, conversation, parallel=False):
    # deprecated
    print("Function plan_pages is deprecated. Use plan_pages_threadable instead.")
    raise NotImplementedError
    num_pages = cfg["page_count"]
    page_contents = [None] * num_pages
    if parallel:
        # Create a pool of worker processes based on the number of pages
        with multiprocessing.Pool(processes=num_pages) as pool:
            # Create a list of arguments for each call to plan_single_page
            args_list = [
                (i, page["requirements"], conversation, page_contents)
                for i, page in enumerate(cfg["pages"])
            ]
            # Use starmap for functions with multiple arguments
            pool.starmap(plan_single_page, args_list)
    else:
        for i, page in enumerate(cfg["pages"]):
            page_cfg = page["requirements"]
            plan_single_page(i, page_cfg, conversation, page_contents)
    return page_contents


def plan_fonts(cfg, conversation):
    conv = ClaudeConversation()
    conv.conversation = conversation
    template = font_choice_prompt
    font_choice = conv.add_message(human_message=template)

    font_choice = fuzzymatch_fontchoice(font_choice, dict_with_font_choices)

    return font_choice


def plan_image_styles(cfg, summary):
    # raise NotImplementedError
    conv = ClaudeConversation()
    conv.conversation = summary
    template = image_stylistic_template
    image_style = conv.add_message(human_message=template)
    image_style = extract_style_reply(image_style)
    return image_style


def generate_content(project_cfg, layout_cfg, verbose=False):
    # deprecated
    # raise deprecated warning
    print("Deprecated function. Use generate_content_threadable instead.")
    raise NotImplementedError
    # wrap this function in a threadable function

    num_pages = project_cfg["page_count"]
    page_contents = [None] * num_pages
    content = {
        "pdf_text": None,
        "sample": None,
        "summary": None,
        "page_contents": page_contents,
    }
    generate_content_threadable(project_cfg, layout_cfg, content, verbose=verbose)
    return content


def check_content_dir(cfg, write_to_file=True):
    if write_to_file:
        # create dir if it doesn't exist
        if not os.path.exists("outputs"):
            os.makedirs("outputs")

        # outputs/<project_id> dir

        if not os.path.exists(f"outputs/{cfg['project_id']}"):
            os.makedirs(f"outputs/{cfg['project_id']}")

        # conters dir
        if not os.path.exists(f"outputs/{cfg['project_id']}/content"):
            os.makedirs(f"outputs/{cfg['project_id']}/content")

    # return path to content dir
    return f"outputs/{cfg['project_id']}/content"


def plan_single_page_threadable(page_number, page_cfg, conversation, page_contents):
    conv = ClaudeConversation()
    conv.conversation = conversation
    page_template = get_page_template(page_number, page_cfg)
    page_plan_text = conv.add_message(human_message=page_template, asst_message="<")
    new_page_content = extract_page_reply(page_plan_text)

    # Lock only the part where we update the shared data
    with lock:
        page_contents[page_number] = new_page_content


def plan_pages_threadable(cfg, conversation, page_contents):
    num_pages = cfg["page_count"]

    if "parallel" in cfg and cfg["parallel"]:
        # Create a pool of worker processes based on the number of pages
        with multiprocessing.Pool(processes=num_pages) as pool:
            # Create a list of arguments for each call to plan_single_page
            args_list = [
                (i, page["requirements"], conversation, page_contents)
                for i, page in enumerate(cfg["pages"])
            ]
            # Use starmap for functions with multiple arguments
            pool.starmap(plan_single_page_threadable, args_list)
    else:
        for i, page in enumerate(cfg["pages"]):
            page_cfg = page["requirements"]
            plan_single_page_threadable(i, page_cfg, conversation, page_contents)


def generate_content_threadable(
    project_cfg, layout_cfg, content, verbose=True, write_to_file=True
):
    # full_cfg = dict()
    full_cfg = {**project_cfg, **layout_cfg}

    full_cfg["pdf_text"] = content["pdf_text"]
    full_cfg["sample"] = content["sample"]

    path = None
    if write_to_file:
        path = check_content_dir(project_cfg)

        # write pdf_text to file
        with open(f"{path}/pdf_text.txt", "w") as f:
            full_cfg["pdf_text"] = full_cfg["pdf_text"].encode('utf-16','surrogatepass').decode('utf-16')
            f.write(full_cfg["pdf_text"])

        # write sample to file
        with open(f"{path}/sample.txt", "w") as f:
            full_cfg["sample"] = full_cfg["sample"].encode('utf-16','surrogatepass').decode('utf-16')
            f.write(full_cfg["sample"])

    summary = summarize_zine(full_cfg)

    with lock:
        content["summary"] = summary

    if verbose:
        print("Summary generated successfully")
        print("Summary: ", summary[:100])
        print("\n\n")

    if write_to_file:
        with open(f"{path}/summary.txt", "w") as f:
            f.write(summary)

    with lock:
        if "page_contents" not in content:
            content["page_contents"] = [None] * full_cfg["page_count"]

    plan_pages_threadable(full_cfg, summary, content["page_contents"])

    if write_to_file:
        for i, page in enumerate(content["page_contents"]):
            # write to json
            with open(f"{path}/page_{i}_content.json", "w") as f:
                json.dump(page, f)

    fonts = plan_fonts(full_cfg, summary)
    image_styles = plan_image_styles(full_cfg, summary)

    with lock:
        content["fonts"] = fonts
        content["image_styles"] = image_styles

    if write_to_file:
        with open(f"{path}/fonts.txt", "w") as f:
            f.write(fonts)

        # save image_styles to json file
        with open(f"{path}/image_styles.json", "w") as f:
            json.dump(image_styles, f)

        with open(f"{path}/content.json", "w") as f:
            json.dump(content, f, indent=4)