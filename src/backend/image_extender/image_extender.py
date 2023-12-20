from PIL import Image
from abc import ABC, abstractmethod

from rich.console import Console

"""
Image Extender is an abstract class that defines the interface for all image extenders
"""
class ImageExtender(ABC):

    def __init__(self, cfg):
        self.cfg = cfg
        self.console = Console()

    @abstractmethod
    def extend_up(self, img: Image, prompt: str, additional_height: int) -> Image:
        pass

    @abstractmethod
    def extend_down(self, img: Image, prompt: str, additional_height: int) -> Image:
        pass