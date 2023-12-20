import torch
import os
from .image_generators import get_image_generator

import base64
import requests


def generate_images(project_cfg, content):
    image_generator = get_image_generator(project_cfg["image_generator"])

    page_contents = content["page_contents"]

    output = {"img_paths": []}

    for i, page_content in enumerate(page_contents):
        img_descriptions = page_content["image_description"]
        img_phrases = page_content["image_phrases"]

        img_paths = []

        for j, (img_description, img_phrase) in enumerate(
            zip(img_descriptions, img_phrases)
        ):
            img_description = (
                img_description.strip()
                + ". The style is "
                + content["image_styles"]["style_phrases"]
            )

            print("Image description: ", img_description)

            if i > 0:
                img = image_generator.make_image(img_description)  # PIL image
            else:
                img = image_generator.make_image(img_description, width=512, height=768)

            img_out_path = f"outputs/{project_cfg['project_id']}/images/"

            if not os.path.exists(img_out_path):
                os.makedirs(img_out_path)

            img_out_path = os.path.join(img_out_path, f"page_{i}_img_{j}.png")
            img.save(img_out_path)

            img_paths.append(img_out_path)

        output["img_paths"].append(img_paths)

    del image_generator
    torch.cuda.empty_cache()

    return output


def stability_api(texts: list) -> list:
    # Constants and configurations
    engine_id = "stable-diffusion-xl-1024-v1-0"
    api_host = os.getenv("API_HOST", "https://api.stability.ai")
    api_key = "sk-QJI455Lc4ktq2dAAmym0IQBLXGYsiZAnArDll1z7qseXynmc"
    if api_key is None:
        raise Exception("Missing Stability API key.")

    # Prepare text prompts for API
    text_prompts = [{"text": text} for text in texts]

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json={
            "text_prompts": text_prompts,
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        },
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

    images_binary_data = [
        base64.b64decode(image["base64"]) for image in data["artifacts"]
    ]

    return images_binary_data


def generate_images_stability(project_cfg, content):
    # image_generator = get_image_generator(project_cfg["image_generator"])
    page_contents = content["page_contents"]

    output = {"img_paths": []}

    # Step 1: Collect all image descriptions first
    all_descriptions = []
    img_info = (
        []
    )  # This will hold tuples of (page_index, image_index) for each description
    for i, page_content in enumerate(page_contents):
        img_descriptions = page_content["image_description"]
        img_phrases = page_content["image_phrases"]

        for j, (img_description, img_phrase) in enumerate(
            zip(img_descriptions, img_phrases)
        ):
            img_description = (
                img_description.strip()
                + ". The style is "
                + content["image_styles"]["style_phrases"]
            )
            all_descriptions.append(img_description)
            img_info.append((i, j))

    # Step 2: Call the image generation API once with all the prompts
    all_images = stability_api(all_descriptions)

    # Step 3: Distribute the generated images back to their appropriate places
    for (page_index, image_index), img_data in zip(img_info, all_images):
        img_out_path = f"outputs/{project_cfg['project_id']}/images/"
        if not os.path.exists(img_out_path):
            os.makedirs(img_out_path)

        img_out_file = os.path.join(
            img_out_path, f"page_{page_index}_img_{image_index}.png"
        )

        with open(img_out_file, "wb") as f:
            f.write(img_data)

        if page_index >= len(output["img_paths"]):
            output["img_paths"].append([])
        output["img_paths"][page_index].append(img_out_file)

    # del image_generator
    # torch.cuda.empty_cache()

    return output
