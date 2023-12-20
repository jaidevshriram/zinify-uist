from ZineContent import ZineContent
from ZinePlanner import ZinePlanner
from ..image_generator import add_zine_images
from ..layout_templates.templates import SimpleLayoutTemplate

def create_zine(input_text, style, content_type, content_template, callback=None):
    """
    input_text: input information to be used for generation (research paper, pdf, etc.)
    style: style to be used for generation
    content_type: type of content to be generated
    
    returns: rendered html
    """
    layout = SimpleLayoutTemplate
    zine_content = ZineContent(layout, callback)
    planner = ZinePlanner(input_text, style, content_type, zine_content)
    zine_content = planner.plan_zine()
    add_zine_images(zine_content)
    return zine_content.render()

