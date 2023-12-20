import streamlit as st

import sys
sys.path.append("../")

from backend.image_generator import get_image_generator

st.title("ZINify: Transforming Research Papers into Engaging Zines Using Large Language Models")

cfg = {
    'image_generator': {
        'type': 'stable_diffusion_2',
    }
}

image_generator = get_image_generator(cfg["image_generator"])

# uploaded_files = st.file_uploader("Upload a PDF paper", accept_multiple_files=False)

# if uploaded_files is not None:
#     for uploaded_file in uploaded_files:
#         bytes_data = uploaded_file.read()
#         st.write("filename:", uploaded_file.name)
#         st.write(bytes_data)

prompt = st.text_input("Prompt", "Prompt for image generation")

if prompt is not None:
    image = image_generator.make_image(prompt, 512, 512)
    st.image(image, caption=prompt, use_column_width=True)