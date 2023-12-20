import torch
from diffusers import StableDiffusionInpaintPipeline, EulerAncestralDiscreteScheduler

from PIL import Image
import numpy as np

from requests.exceptions import ChunkedEncodingError

from rich.console import Console

from .image_extender import ImageExtender

class StableDiffusionInpaint(ImageExtender):

    def __init__(self, cfg):
        super().__init__(cfg)
        
        trycnt = 5
        while trycnt > 0:
            try:
                self.pipe = StableDiffusionInpaintPipeline.from_pretrained(
                    "stabilityai/stable-diffusion-2-inpainting",
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                )
                
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

    def extend_up(self, img: Image, prompt: str, additional_height: int) -> Image:
        
        img_np = np.asarray(img)
        img_new_np = np.zeros((img_np.shape[0] + additional_height, img_np.shape[1], 3), dtype=np.uint8)
        img_new_np[additional_height:, :, :] = img_np

        img_new_pil = Image.fromarray(img_new_np[:512, :512, :])

        mask_np = np.zeros((512, 512), dtype=np.uint8)
        mask_np[:additional_height, :] = 1

        mask_image = Image.fromarray(mask_np * 255)

        img_inpainted = self.pipe(
            image=img_new_pil,
            mask_image=mask_image,
            prompt=prompt,
            num_inference_steps=25,
        ).images[0] 

        img_inpainted_np = np.asarray(img_inpainted)

        img_new_np[:additional_height, :, :] = img_inpainted_np[:additional_height, :, :]

        return Image.fromarray(img_new_np)


    def extend_down(self, img: Image, prompt: str, additional_height: int) -> Image:

        img_np = np.asarray(img)
        img_new = np.zeros((img_np.shape[0] + additional_height, img_np.shape[1], 3), dtype=np.uint8)
        img_new[:img_np.shape[0], :, :] = img_np

        img_new = Image.fromarray(img_new[-512, :, :])
        mask = np.zeros((512, 512), dtype=np.uint8)
        mask[-additional_height:, :] = 1

        img_inpainted = self.pipe(
            img_new,
            mask_image=mask,
            prompt=prompt,
            num_inference_steps=25,
        ).images[0] 

        img_inpainted = np.asarray(img_inpainted)

        img_new[-additional_height:, :, :] = img_inpainted[-additional_height:, :, :]

        return Image.fromarray(img_new)