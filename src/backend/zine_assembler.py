import os
import extcolors
import random
import json
from jinja2 import Environment, FileSystemLoader

from PIL import Image
from collections import Counter
from colorsys import rgb_to_hsv, hsv_to_rgb

def get_row_popular_colors(image_path): # computes the most popular quantized color in the bottom row of the image

    # Open the image and convert to RGB
    image = Image.open(image_path).convert("RGB")
    image = image.resize((100, 100))  # Resize for efficiency

    # Extract and quantize pixels
    pixels = [quantize_color(pixel) for pixel in image.getdata()]

    # Consider only the bottom row
    top_row_pixels = pixels[:100]
    bottom_row_pixels = pixels[99*100:]

    # Count occurrences of each pixel color
    color_count_top = Counter(top_row_pixels)
    color_count_bottom = Counter(bottom_row_pixels)

    # Find the most popular color
    most_popular_color_top = color_count_top.most_common(1)[0][0]
    most_popular_color_bottom = color_count_bottom.most_common(1)[0][0]

    return {
        "most_popular_top": most_popular_color_top,
        "most_popular_bottom": most_popular_color_bottom
    }

def quantize_color(color, buckets=50):
    # Calculate the range for each bucket
    range_size = 256 // buckets
    return tuple([(x // range_size) * range_size for x in color])

def get_color_palette(image_path, palette_size=10):
    # Open the image and convert to RGB
    image = Image.open(image_path).convert("RGB")
    image = image.resize((100, 100))  # Resize for efficiency
    
    # Extract and quantize pixels
    pixels = [quantize_color(pixel) for pixel in image.getdata()]
    
    # Count occurrences of each pixel color
    color_count = Counter(pixels)
    
    # Find the most popular color
    most_popular_color = color_count.most_common(1)[0][0]
    
    # Split the image into top and bottom halves
    top_half_pixels = [quantize_color(pixel) for pixel in image.crop((0, 0, 100, 50)).getdata()]
    bottom_half_pixels = [quantize_color(pixel) for pixel in image.crop((0, 50, 100, 100)).getdata()]
    
    # Find the most prominent color in top and bottom halves
    top_half_color = Counter(top_half_pixels).most_common(1)[0][0]
    bottom_half_color = Counter(bottom_half_pixels).most_common(1)[0][0]
    
    return {
        "most_popular": most_popular_color,
        "top_half": top_half_color,
        "bottom_half": bottom_half_color
    }

def contrast_color(input_color):
    # Convert the RGB color to HSV
    hsv = rgb_to_hsv(input_color[0] / 255.0, input_color[1] / 255.0, input_color[2] / 255.0)
    
    # Invert the value for high contrast
    new_hue = (hsv[0] + 0.5) % 1.0
    new_value = 1.0 - hsv[2] if hsv[2] > 0.5 else 1.0  # Ensure the value is high for dark colors
    
    # Convert back to RGB
    contrast_rgb = hsv_to_rgb(new_hue, hsv[1], new_value)
    
    return tuple(int(c * 255) for c in contrast_rgb)

def relative_luminance(rgb):
    """Calculate the relative luminance of a color."""
    r, g, b = [x / 255.0 for x in rgb]
    r = (r / 12.92) if (r <= 0.04045) else ((r + 0.055) / 1.055) ** 2.4
    g = (g / 12.92) if (g <= 0.04045) else ((g + 0.055) / 1.055) ** 2.4
    b = (b / 12.92) if (b <= 0.04045) else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast_ratio(l1, l2):
    """Calculate the contrast ratio between two luminances."""
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)

def best_text_color(bg_rgb, palette):
    """
    Choose the best text color from the palette based on contrast over the given background color.

    Parameters:
    - bg_rgb: RGB tuple of the background color
    - palette: List of RGB tuples representing potential text colors

    Returns:
    - RGB tuple of the selected text color
    """
    bg_luminance = relative_luminance(bg_rgb)
    best_contrast = 0
    best_color = None

    for color, count in palette:
        color_luminance = relative_luminance(color)
        current_contrast = contrast_ratio(bg_luminance, color_luminance)
        
        if current_contrast > best_contrast:
            best_contrast = current_contrast
            best_color = color

    return best_color

def assemble_zine(project_cfg, layout_cfg, content, image_outputs, use_abs_path=True):
    
    # Set up the Jinja2 environment and specify the templates directory
    env = Environment(loader=FileSystemLoader('html_template'))

    # Load font mapping
    with open(os.path.join('html_template', 'font_desc', 'body_fonts.json'), 'r') as f:
        font_mapping = json.load(f)

    if layout_cfg['layout'] == 'single_page_layout':
        sheet1 = env.get_template('base_zine.html')
        web_sheet1 = env.get_template('web_base_zine_1.html')
    else:
        sheet1 = env.get_template('base_zine1_2.html')
        web_sheet1 = env.get_template('web_base_zine_1.html')

    sheet2 = env.get_template('base_zine.html')
    web_sheet2 = env.get_template('web_base_zine_2.html')

    pages_rendered = []
    zine_palette = None

    # Go through all the pages and generate the content
    for page_num in range(len(layout_cfg['pages'])):

        page_layout_path = layout_cfg['pages'][page_num]['html_layout']
        page_layout = env.get_template(page_layout_path)

        page_content = content['page_contents'][page_num]

        args = {
            'title': page_content['title'][0] if len(page_content['title']) > 0 else None,
            'abstract': page_content['abstract'][0] if len(page_content['abstract']) > 0 else None,
        }

        for i, img_path in enumerate(image_outputs['img_paths'][page_num]):
            if use_abs_path:
                args[f'img{i+1}_path'] = os.path.abspath(img_path)
            else:
                args[f'img{i+1}_path'] = img_path

            # Get the color palette for the image
            color_palette = get_color_palette(img_path)
            img = Image.open(img_path).convert("RGB")
            full_color_palette, pixel_count = extcolors.extract_from_image(img, tolerance=32, limit=6)

            if page_num == 0:
                zine_palette = (full_color_palette, pixel_count)

            # Text colour for overlay at the bottom of the image
            text_color = contrast_color(color_palette['bottom_half'])
            args[f'overlay_color{i+1}_bottom'] = f"rgba({text_color[0]}, {text_color[1]}, {text_color[2]}, 1.0)"

            # Text colour for overlay at the top of the image
            text_color = contrast_color(color_palette['top_half'])
            args[f'overlay_color{i+1}_top'] = f"rgba({text_color[0]}, {text_color[1]}, {text_color[2]}, 1.0)"

            # Text colour for overlay at the center of the image
            text_color = contrast_color(color_palette['most_popular'])
            args[f'overlay_color{i+1}_center'] = f"rgba({text_color[0]}, {text_color[1]}, {text_color[2]}, 1.0)"

            # Gradient colours
            args[f'gradient_color{i+1}_top1'] = f"rgba({color_palette['top_half'][0]}, {color_palette['top_half'][1]}, {color_palette['top_half'][2]}, 1.0)"
            args[f'gradient_color{i+1}_top0'] = f"rgba({color_palette['top_half'][0]}, {color_palette['top_half'][1]}, {color_palette['top_half'][2]}, 0.0)"

            args[f'gradient_color{i+1}_bottom1'] = f"rgba({color_palette['bottom_half'][0]}, {color_palette['bottom_half'][1]}, {color_palette['bottom_half'][2]}, 1.0)"
            args[f'gradient_color{i+1}_bottom0'] = f"rgba({color_palette['bottom_half'][0]}, {color_palette['bottom_half'][1]}, {color_palette['bottom_half'][2]}, 0.0)"

            args[f'gradient_color{i+1}_center1'] = f"rgba({color_palette['most_popular'][0]}, {color_palette['most_popular'][1]}, {color_palette['most_popular'][2]}, 1.0)"
            args[f'gradient_color{i+1}_center0'] = f"rgba({color_palette['most_popular'][0]}, {color_palette['most_popular'][1]}, {color_palette['most_popular'][2]}, 0.0)"

            # Compute a good background colour for the page - if the image is on top, use a colour from the bottom row of the image, and vice versa
            row_popular_colors = get_row_popular_colors(img_path)

            # If image is at top, set the background colour to the most popular colour in the bottom row of the image
            args[f'background_color{i+1}_topimage'] = f"rgba({row_popular_colors['most_popular_bottom'][0]}, {row_popular_colors['most_popular_bottom'][1]}, {row_popular_colors['most_popular_bottom'][2]}, 1.0)"
            
            # If image is at bottom, set the background colour to the most popular colour in the top row of the image
            args[f'background_color{i+1}_bottomimage'] = f"rgba({row_popular_colors['most_popular_top'][0]}, {row_popular_colors['most_popular_top'][1]}, {row_popular_colors['most_popular_top'][2]}, 1.0)"

            text_color_imgtop = best_text_color(row_popular_colors['most_popular_bottom'], zine_palette[0])
            text_color_imgbottom = best_text_color(row_popular_colors['most_popular_top'], zine_palette[0])

            args[f'text_color{i+1}_topimage'] = f"rgba({text_color_imgtop[0]}, {text_color_imgtop[1]}, {text_color_imgtop[2]}, 1.0)"
            args[f'text_color{i+1}_bottomimage'] = f"rgba({text_color_imgbottom[0]}, {text_color_imgbottom[1]}, {text_color_imgbottom[2]}, 1.0)"

            # Choose a random zine palette colour for the background
            bg_color, count = random.choice(zine_palette[0])
            args[f'background_color{i+1}'] = f"rgba({bg_color[0]}, {bg_color[1]}, {bg_color[2]}, 1.0)"
            args[f'background_color{i+1}_tuple'] = f"{bg_color[0]}, {bg_color[1]}, {bg_color[2]}"
            text_color = best_text_color(bg_color, zine_palette[0])
            args[f'text_color{i+1}'] = f"rgba({text_color[0]}, {text_color[1]}, {text_color[2]}, 1.0)"

        for i, heading in enumerate(page_content['heading']):
            args[f'heading{i+1}'] = heading

        for i, text in enumerate(page_content['body_texts']):
            args[f'text{i+1}'] = text

        for i, catchy_text in enumerate(page_content['catchy_text']):
            args[f'catchy_text{i+1}'] = catchy_text

        page_render = page_layout.render(**args)

        pages_rendered.append(page_render)

    args['title_font'] = content['fonts']
    args['body_font'] = font_mapping[content['fonts']]

    # Render the final zine
    if layout_cfg['layout'] == 'single_page_layout':

        web_sheet1 = web_sheet1.render(page1=pages_rendered[0], page2=pages_rendered[1], page3=pages_rendered[2], title_font=args['title_font'], body_font=args['body_font'])
        web_sheet2 = web_sheet2.render(page1=pages_rendered[3], page2=pages_rendered[4], page3=pages_rendered[5], title_font=args['title_font'], body_font=args['body_font'])

        pages_rendered = [pages_rendered[4], pages_rendered[5], pages_rendered[0], pages_rendered[1], pages_rendered[2], pages_rendered[3]]
        sheet1 = sheet1.render(page1=pages_rendered[0], page2=pages_rendered[1], page3=pages_rendered[2], title_font=args['title_font'], body_font=args['body_font'])
        sheet2 = sheet2.render(page1=pages_rendered[3], page2=pages_rendered[4], page3=pages_rendered[5], title_font=args['title_font'], body_font=args['body_font'])
        
    elif layout_cfg['layout'] == 'double_page_layout':
        raise NotImplementedError("Order not determined for 2 page")

        web_sheet1 = web_sheet1.render(page1=pages_rendered[0], page2=pages_rendered[1], title_font=args['title_font'], body_font=args['body_font'])
        web_sheet2 = web_sheet2.render(page1=pages_rendered[2], page2=pages_rendered[3], title_font=args['title_font'], body_font=args['body_font'])

        sheet1 = sheet1.render(page1=pages_rendered[0], page2=pages_rendered[1], title_font=args['title_font'], body_font=args['body_font'])
        sheet2 = sheet2.render(page1=pages_rendered[2], page2=pages_rendered[3], page3=pages_rendered[4], title_font=args['title_font'], body_font=args['body_font'])

    return {
        'web_sheet': [web_sheet1, web_sheet2],
        'sheet': [sheet1, sheet2]
    }