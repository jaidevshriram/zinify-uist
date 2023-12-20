from .stable_diffusion_2 import StableDiffusion2
from .stable_diffusion_xl import StableDiffusionXL
from .pano_stable_diffusion import StableDiffusionPano
from .dalle3 import Dalle3

def get_image_generator(cfg):
    
    type = cfg["type"]

    if type == "stable_diffusion_2":
        return StableDiffusion2(cfg)
    elif type == "stable_diffusion_xl":
        return StableDiffusionXL(cfg)
    elif type == "stable_diffusion_pano":
        return StableDiffusionPano(cfg)
    elif type == "dalle3":
        return Dalle3(cfg)
    else:
        raise ValueError(f"Unknown image generator type: {type}")
    

def add_zine_images(zine_content, batch_size=1):
    """
    zine_content: ZineContent object

    Adds image paths to zine_content object.     
    returns updated zine_content object
    """

    raise NotImplementedError