from .stable_diffusion_inpaint import StableDiffusionInpaint

def get_image_extender(cfg):
    
    return StableDiffusionInpaint(cfg)