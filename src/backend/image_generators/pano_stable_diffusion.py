import torch
from diffusers import StableDiffusionPanoramaPipeline, DDIMScheduler, EulerAncestralDiscreteScheduler
import time
from .generator import ImageGenerator

from requests.exceptions import ChunkedEncodingError

from rich.console import Console

class StableDiffusionPano(ImageGenerator):

    def __init__(self, cfg):
        super().__init__(cfg)
        
        trycnt = 5
        while trycnt > 0:
            try:
                model_ckpt = "stabilityai/stable-diffusion-2-base"
                self.pipe = StableDiffusionPanoramaPipeline.from_pretrained(
                    model_ckpt, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                )
                self.pipe.scheduler = DDIMScheduler.from_config(self.pipe.scheduler.config)
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

    def make_image(self, prompt: str, height: int, width: int):

        image = self.pipe(prompt=prompt, height=height, width=width, num_inference_steps=25).images[0]
        
        return image