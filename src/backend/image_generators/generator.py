from PIL import Image
from abc import ABC, abstractmethod

from rich.console import Console

"""
ImageGenerator is an abstract class that defines the interface for all image generators.pi
"""
class ImageGenerator(ABC):

    def __init__(self, cfg):
        self.cfg = cfg
        self.console = Console()

    @abstractmethod
    def make_image(self, prompt: str, height: int, width: int) -> Image:
        pass