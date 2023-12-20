import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler, EulerAncestralDiscreteScheduler

from .generator import ImageGenerator

from requests.exceptions import ChunkedEncodingError

from rich.console import Console

class StableDiffusion2(ImageGenerator):

    def __init__(self, cfg):
        super().__init__(cfg)
        
        trycnt = 5
        while trycnt > 0:
            try:
                self.pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2-1", torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
                self.pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(self.pipe.scheduler.config)
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

        if height != width or height != 512:
            raise Warning("StableDiffusion2 only supports a fixed siz of 512x512, will resize to height, width")

        image = self.pipe(prompt=prompt, height=height, width=width, num_inference_steps=25).images[0]

        image = image.resize((height, width))
        
        return image