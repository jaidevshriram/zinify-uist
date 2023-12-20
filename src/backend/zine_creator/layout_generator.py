import os
import random
import json

LAYOUT_BASE = "html_template/"

def get_layout_requirements(file):

    # Get file name without extension
    file_name = os.path.splitext(file)[0]

    # Get the corresponding requirements for this config
    with open(os.path.join(LAYOUT_BASE, os.path.join("reqs"), f"{file_name}.json")) as f:
        requirements = json.load(f)

    return requirements

def get_front_page_layout(project_cfg):

    FRONT_FOLDER = "cover/"

    # Get list of files in this template folder
    files = os.listdir(os.path.join(LAYOUT_BASE, FRONT_FOLDER))

    # Select a random file
    file = random.choice(files)

    # Get the corresponding requirements for this config
    requirements = get_layout_requirements(file)

    page_cfg = {
        'html_layout': os.path.join(FRONT_FOLDER, file),
        'requirements': requirements
    }

    return page_cfg

def get_two_page_layout(project_cfg):

    TWO_PAGE_FOLDER = "two_page_layout/"

    # Get list of files in this template folder
    files = os.listdir(os.path.join(LAYOUT_BASE, TWO_PAGE_FOLDER))

    # Select a random file
    file = random.choice(files)
    requirements = get_layout_requirements(file)

    page_cfg = {
        # 'html_layout': os.path.join(TWO_PAGE_FOLDER, file),
        'html_layout': os.path.join(TWO_PAGE_FOLDER, 'twopage_2.html'),
        'requirements': requirements
    }

    return page_cfg

def get_page_layout(project_cfg):

    PAGE_FOLDER = "content/"

    # Get list of files in this template folder
    files = os.listdir(os.path.join(LAYOUT_BASE, PAGE_FOLDER))

    # Select a random file
    file = random.choice(files)
    requirements = get_layout_requirements(file)

    page_cfg = {
        'html_layout': os.path.join(PAGE_FOLDER, file),
        'requirements': requirements
    }

    return page_cfg

def get_back_page_layout(project_cfg):

    BACK_FOLDER = "back/"

    # Get list of files in this template folder
    files = os.listdir(os.path.join(LAYOUT_BASE, BACK_FOLDER))

    # Select a random file
    file = random.choice(files)
    requirements = get_layout_requirements(file)

    page_cfg = {
        'html_layout': os.path.join(BACK_FOLDER, file),
        'requirements': requirements
    }

    return page_cfg

def single_page_layout(project_cfg):

    page_layout_configs = []

    # Front page
    front_page = get_front_page_layout(project_cfg)
    page_layout_configs.append(front_page)

    # Page 2-5
    for i in range(4):
        page_layout = get_page_layout(project_cfg)
        while page_layout == page_layout_configs[-1]:
            page_layout = get_page_layout(project_cfg)
        page_layout_configs.append(page_layout)

    # Page 6
    back_page = get_back_page_layout(project_cfg)
    page_layout_configs.append(back_page)

    return {
        'pages': page_layout_configs
    }

def double_page_layout(project_cfg):

    page_layout_configs = []

    # Front page
    front_page = get_front_page_layout(project_cfg)
    page_layout_configs.append(front_page)

    # Page 2-3
    page_layout = get_two_page_layout(project_cfg)
    page_layout_configs.append(page_layout)

    # 4-5
    for i in range(2):
        page_layout = get_page_layout(project_cfg)
        while page_layout == page_layout_configs[-1]:
            page_layout = get_page_layout(project_cfg)
        page_layout_configs.append(page_layout)

    # Page 6
    back_page = get_back_page_layout(project_cfg)
    page_layout_configs.append(back_page)

    return {
        'pages': page_layout_configs
    }

def generate_layout(project_cfg):

    # Select a random layout - 80% chance of single page layout, 20% chance of two page layout
    # layout = single_page_layout if random.random() < 0.8 else two_page_layout
    # layout = double_page_layout
    layout = single_page_layout

    # Generate the layout
    layout_cfg = layout(project_cfg)
    layout_cfg['layout'] = layout.__name__

    if not os.path.exists(os.path.join("outputs", project_cfg['project_id'])):
        os.makedirs(os.path.join("outputs", project_cfg['project_id']), exist_ok=True)

    # Write the layout to a file
    with open(os.path.join("outputs", project_cfg['project_id'], "layout.json"), 'w') as f:
        f.write(json.dumps(layout_cfg, indent=4))

    return layout_cfg