import os
import base64
import requests

from PIL import Image
import numpy as np


import base64
import os
import requests
from concurrent.futures import ThreadPoolExecutor


def image_to_byte_array(image: Image) -> bytes:
  # BytesIO is a file-like buffer stored in memory
  imgByteArr = io.BytesIO()
  # image.save expects a file-like as a argument
  image.save(imgByteArr, format=image.format)
  # Turn the BytesIO object back into a bytes object
  imgByteArr = imgByteArr.getvalue()
  return imgByteArr

def fetch_single_image(text: str) -> bytes:
    # Constants and configurations
    engine_id = "stable-diffusion-xl-1024-v1-0"
    api_host = os.getenv("API_HOST", "https://api.stability.ai")
    api_key = "sk-QJI455Lc4ktq2dAAmym0IQBLXGYsiZAnArDll1z7qseXynmc"

    if api_key is None:
        raise Exception("Missing Stability API key.")

    # clean text
    text = text.replace("\n", " ")
    text = text.replace('"', " ")
    # text =

    print(text)
    
    # Prepare text prompt for API
    text_prompt = {"text": text}

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json={
            "text_prompts": [text_prompt],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        },
    )

    if response.status_code != 200:
        print(response.status_code)
        print(f"Non-200 response for text '{text}': " + str(response.text))

        response = requests.post(
            f"{api_host}/v1/generation/{engine_id}/text-to-image",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "text_prompts": [{"text": "A blank image"}],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30,
            },
        )    

        if response.status_code != 200:
            print(response.status_code)
            print(f"Non-200 response for text A blank image': " + str(response.text))
            raise Exception("Non-200 response from Stability API.")

    data = response.json()
    image_binary_data = base64.b64decode(data["artifacts"][0]["base64"])

    return image_binary_data


def stability_api(texts: list) -> list:
    with ThreadPoolExecutor() as executor:
        images_binary_data = list(executor.map(fetch_single_image, texts))

    assert len(images_binary_data) == len(texts)

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
    output = {"img_paths": [[] for _ in range(len(page_contents))]}


    for (page_index, image_index), img_data in zip(img_info, all_images):
        img_out_path = f"outputs/{project_cfg['project_id']}/images/"
        if not os.path.exists(img_out_path):
            os.makedirs(img_out_path)

        img_out_file = os.path.join(
            img_out_path, f"page_{page_index}_img_{image_index}.png"
        )

        img_path = f"page_{page_index}_img_{image_index}.png"

        with open(img_out_file, "wb") as f:
            f.write(img_data)

        # write to static folder
        with open("static/" + img_path, "wb") as f:
            f.write(img_data)

        output["img_paths"][page_index].append("static/" + img_path)

    # del image_generator
    # torch.cuda.empty_cache()

    return output

if __name__ == "__main__":

    prompt = 'A happy monster scientist presents their zine to a group of monster children. The scientist holds up the colorful zine proudly, with a big smile on their fuzzy blue face. The zine has a fun cover with the title "Research Paper Party!" in bubbly font. The monster kids gaze at the zine in wonder, with wide eyes and excited smiles. They are gathered in a playroom with toys, books, and games scattered around.. The style is thick outlines, flat colors, simple shapes, cartoony, whimsical, playful, minimalist, colorful'
    # prompt = 'cat'

    fetch_single_image(prompt)