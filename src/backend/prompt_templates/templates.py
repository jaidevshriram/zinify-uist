import re

import fuzzywuzzy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

summarize_template = "Create a very detailed summary of this paper. Include the main concepts and mathematical equations if any. Additionally, extract the abstract word for word."

style_clarification = "The text and the images of the zine however should be purely academic - covering the main concepts and equations. Do not build a story, analogy or metaphor in the text or image prompts. The image prompts should be very explicit with obviously visualizable wording. The images prompts should all have a consistent color palette."

zine_type_templates = {
    "summary": f"with the aim of creating a zine that offers an overview ( outlines the main objectives and scope). {style_clarification}",
    "primer": f"with the aim of creating a zine that serves as a primer (offers foundational knowledge and context for the topic). {style_clarification}",
    "highlight": f"with the aim of creating a zine that highlights key takeaways (emphasizes novel contributions and primary results). {style_clarification}",
    "creative": "with the aim of creating a zine that is creative (builds an analogy, metaphor, story ..etc based on the style to explain the topic)",
}

zine_plan_template = "Plan a {page_count} page zine of the paper in a '{style}' style {content_type}. For each page of the zine, provide thorough text summaries of the concepts discussed (not just description of the text). Additionally, include ideas for images and a description of the style of the images. All images should maintain a consistent style. The zine should begin with a title on the first page and conclude with its abstract on the last page"

page_start_template = "Please create the page {i} of this zine."

page_content_template = "This page will include {image_count} image(s)"


page_heading_text_template = "{heading_count} heading like text(s) for the page"

page_catchy_text_template = "a short catchy piece of text (short phrase, headings)"

page_body_text_template = "{long_count} piece(s) of text for the body (3-4 sentences)"

page_title_text_template = "a catchy zine title"

page_abstract_text_template = "the zine abstract"


page_format_template = "All zine text is final and must be high-quality (not instructions or descriptions). You will reply exactly in the format below and with nothing else."


page_image_format_template = "<image{i}> (detailed stand alone image description that is and easily visualizable, with style and color information. The image should not have text.) </image{i}>"

page_heading_format_template = "<heading{i}> (heading like text) </heading{i}>"

page_catchy_format_template = "<catchy> (short catchy text) </catchy>"

page_body_format_template = "<body{i}> (body text - 3,4 sentences) </body{i}>"

page_title_format_template = "<title> (catchy zine title) </title>"

page_abstract_format_template = (
    "<abstract> (zine abstract shortened to 4-5 sentences) </abstract>"
)

page_image_phrase_format_template = "<image_phrases{i}> (image{i} descrition condensed to phrases with stylistic phrases) </image_phrases{i}>"


def get_zine_plan_template(page_count, style, content_type):
    assert content_type in zine_type_templates.keys()
    return zine_plan_template.format(
        page_count=(page_count),
        style=style,
        content_type=zine_type_templates[content_type],
    )


def get_page_template(page_num, cfg):
    image_count = cfg["num_images"]
    catchy_text_count = cfg["catchy_text"]
    body_text_count = cfg["text_boxes"]
    titles_count = cfg["title"]
    abstracts_count = cfg["abstract"]
    headings_count = cfg["heading"]

    template = page_start_template.format(i=page_num + 1)  # 0 indexed
    template += " "
    template += page_content_template.format(image_count=image_count)

    if headings_count > 0:
        template += " and "
        template += page_heading_text_template.format(heading_count=headings_count)

    if body_text_count > 0:
        template += " and "
        template += page_body_text_template.format(long_count=body_text_count)

    if titles_count > 0:
        template += " and "
        template += page_title_text_template

    if abstracts_count > 0:
        template += " and "
        template += page_abstract_text_template

    if catchy_text_count > 0:
        template += " and "
        template += page_catchy_text_template

    template += ". "
    template += page_format_template
    template += "\n"
    for i in range(1, image_count + 1):
        template += page_image_format_template.format(i=i)
        template += "\n"
        template += page_image_phrase_format_template.format(i=i)
        template += "\n"

    for i in range(1, headings_count + 1):
        template += page_heading_format_template.format(i=i)
        template += "\n"

    for i in range(1, body_text_count + 1):
        template += page_body_format_template.format(i=i)
        template += "\n"

    if titles_count > 0:
        template += page_title_format_template
        template += "\n"

    if abstracts_count > 0:
        template += page_abstract_format_template
        template += "\n"

    if catchy_text_count > 0:
        template += page_catchy_format_template
        template += "\n"

    return template.strip()


font_choices = """Arial        - Clean and modern sans-serif font.
Verdana      - Popular sans-serif font for web use.
Times        - Timeless and classic serif font.
Courier      - Monospace font, ideal for coding.
Georgia      - Elegant and readable serif font.
Tahoma       - Compact sans-serif font.
Lucida       - Versatile family with both serif and sans-serif styles.
Impact       - Thick and bold font for strong headlines.
Garamond     - Old-style serif font, perfect for literature.
ComicSans    - Playful and informal font (use with caution!)."""


def generate_font_choices(dict_with_font_choices):
    font_choices = ""
    for key in dict_with_font_choices:
        font_choices += key.strip() + " - " + dict_with_font_choices[key].strip() + "\n"
    return font_choices

#raise NotImplementedError
# dict_with_font_choices = {
#     "Arial": "Clean and modern sans-serif font.",
#     "Verdana": "Popular sans-serif font for web use.",
#     "Times": "Timeless and classic serif font.",
#     "Courier": "Monospace font, ideal for coding.",
#     "Georgia": "Elegant and readable serif font.",
#     "Tahoma": "Compact sans-serif font.",
# }

dict_with_font_choices = {
    "Cute Notes": "Block letters, almost cartoony in appearance",
    "Magazine Letter By Brntlbrnl": "Scrap book style letters, very newspaper, rough in appearance, block letters",
    "Seagram Tfb": "Caligraphy style, very fancy, old style,",
    "Pixeled": "Pixelated, 8 bit, old school, video game style",
    "Perfect Beloved": "Cursive, handwritten, very elegant, personal"
}

assert dict_with_font_choices is not None, "dict_with_font_choices is None. Please set it to a dictionary with font names as keys and descriptions as values."

#raise

font_choices = generate_font_choices(dict_with_font_choices)


font_choice_prompt = (
    f"Choose a font that matches the image style for the zine from the list below.\n\n {font_choices} \n\n"
    + "Reply with the name (only the name) of the font exactly as it appears in the list above. Your reply should only be the name of the font and nothing else."
)


def fuzzymatch_fontchoice(font_choice, font_choices_dict):
    font_choices = list(font_choices_dict.keys())

    if font_choice in font_choices:
        return font_choice

    # if not found, fuzzy match
    font_choice = process.extractOne(font_choice, font_choices)[0]
    return font_choice


image_stylistic_template = """Describe the artistic style of the images and color palette in the zine. You will reply exactly in the format below and with nothing else.
<style> (description of the style) </style>
<style_phrases> (description of the style condensed to phrases) </style_phrases>"""


import re


def remove_newlines_between_tags(text):
    # This pattern captures the content between '>' and '</' and removes newlines from it
    pattern = r"(>)([^<]*)(<\/)"
    repl = lambda m: m.group(1) + m.group(2).replace("\n", "") + m.group(3)
    return re.sub(pattern, repl, text)


def extract_page_reply(text):
    text = remove_newlines_between_tags(text)

    image_count = 0
    image_phrases_count = 0
    short_count = 0
    long_count = 0
    heading_count = 0
    body_count = 0
    title_count = 0
    abstract_count = 0
    catchy_count = 0

    image_descriptions = []
    image_phrases = []
    short_texts = []
    long_texts = []
    heading_texts = []
    body_texts = []
    title_texts = []
    abstract_texts = []
    catchy_texts = []

    lines = text.strip().split("\n")

    for line in lines:
        image_match = re.search(r"<image(\d+)>.*</image(\d+)>", line)
        image_phrases_match = re.search(
            r"<image_phrases(\d+)>.*</image_phrases(\d+)>", line
        )
        heading_match = re.search(r"<heading(\d+)>.*</heading(\d+)>", line)
        body_match = re.search(r"<body(\d+)>.*</body(\d+)>", line)
        title_match = re.search(r"<title>.*</title>", line)
        abstract_match = re.search(r"<abstract>.*</abstract>", line)
        catchy_match = re.search(r"<catchy>.*</catchy>", line)

        if image_match:
            image_count += 1
            desc = re.sub(r"<image\d+>|</image\d+>", "", line).strip()
            image_descriptions.append(desc)

        elif image_phrases_match:
            image_phrases_count += 1
            desc = re.sub(r"<image_phrases\d+>|</image_phrases\d+>", "", line).strip()
            image_phrases.append(desc)

        elif heading_match:
            heading_count += 1
            txt = re.sub(r"<heading\d+>|</heading\d+>", "", line).strip()
            heading_texts.append(txt)

        elif body_match:
            body_count += 1
            txt = re.sub(r"<body\d+>|</body\d+>", "", line).strip()
            body_texts.append(txt)

        elif title_match:
            title_count += 1
            txt = re.sub(r"<title>|</title>", "", line).strip()
            title_texts.append(txt)

        elif abstract_match:
            abstract_count += 1
            txt = re.sub(r"<abstract>|</abstract>", "", line).strip()
            abstract_texts.append(txt)

        elif catchy_match:
            catchy_count += 1
            txt = re.sub(r"<catchy>|</catchy>", "", line).strip()
            catchy_texts.append(txt)

    assert image_count == len(image_descriptions)
    assert image_phrases_count == len(image_phrases)

    return {
        "image_description": image_descriptions,
        "image_phrases": image_phrases,
        # "short_texts": short_texts,
        # "long_texts": long_texts,
        "heading": heading_texts,
        "body_texts": body_texts,
        "title": title_texts,
        "abstract": abstract_texts,
        "catchy_text": catchy_texts,
    }


def extract_style_reply(text):
    text = remove_newlines_between_tags(text)

    # use regex to find the tags
    # return the lists
    style_match = re.search(r"<style>.*</style>", text)
    style_phrases_match = re.search(r"<style_phrases>.*</style_phrases>", text)

    if style_match:
        style = style_match.group(0)
        # remove the tags
        style = style.replace("<style>", "")
        style = style.replace("</style>", "")
        style = style.strip()

    if style_phrases_match:
        style_phrases = style_phrases_match.group(0)
        # remove the tags
        style_phrases = style_phrases.replace("<style_phrases>", "")
        style_phrases = style_phrases.replace("</style_phrases>", "")
        style_phrases = style_phrases.strip()

    return {"style": style, "style_phrases": style_phrases}


if __name__ == "__main__":
    sample_cfg = {
        "title": 1,
        "abstract": 1,
        "heading": 1,
        "catchy_text": 1,
        "num_images": 1,
        "text_boxes": 1,
        "word_count": [30, 5],
    }

    print(get_zine_plan_template(4, "minimalist", "summary"))
    print("\n\n")
    print(get_page_template(0, sample_cfg))
    print("\n\n")
    print(image_stylistic_template)
    print("\n\n")
    print(
        extract_page_reply(
            """<image1> (detailed stand alone image description including stylistic and thematic description) </image1>
<image_phrases1> (image1 descrition condensed to phrases with stylistic phrases) </image_phrases1>
<image2> (detailed stand alone image description including stylistic and thematic description) </image2>
<image_phrases2> (image2 descrition condensed to phrases with stylistic phrases) </image_phrases2>
<short1> (short text) </short1>
<abstract> (long text) </abstract>"""
        )
    )
    print("\n\n")
    print(
        extract_style_reply(
            """<style> (description of the style) </style>
<style_phrases> (description of the style condensed to phrases) </style_phrases>"""
        )
    )
