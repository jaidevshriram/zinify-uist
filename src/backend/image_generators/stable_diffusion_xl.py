import torch
from PIL import Image

from requests.exceptions import ChunkedEncodingError

from diffusers import StableDiffusionXLPipeline

from .generator import ImageGenerator

class StableDiffusionXL(ImageGenerator):

    def __init__(self, cfg):
        super().__init__(cfg)
        
        trycnt = 1

        while trycnt > 0:
            try:
                self.pipe = StableDiffusionXLPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32, safety_checker=None)
                if torch.cuda.is_available():
                    self.pipe = self.pipe.to("cuda")
                elif torch.backends.mps.is_available():
                    self.pipe = self.pipe.to("mps")

                break
            except ChunkedEncodingError as ex:
                if trycnt <= 0:
                    raise ex
                else:
                    time.sleep(0.5)
                trycnt -= 1

        self.console.print("[bold green]Loaded stable diffusion.[/bold green]")

    def make_image(self, prompt: str, height: int=1024, width: int=1024) -> Image:

        # if height != width or height != 1024:
        #     print("StableDiffusion XL only supports a fixed size of 1024x1024, will resize to height, width")

        image = self.pipe(prompt=prompt, height=height, width=width, num_inference_steps=25).images[0]

        image = image.resize((width, height))
        
        return image