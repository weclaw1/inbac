from typing import Optional, List, Tuple, Any
from argparse import Namespace
from PIL import Image
from PIL.ImageTk import PhotoImage


class Model():
    def __init__(self, args):
        self.args: Namespace = args
        self.images: List[str] = []
        self.selection_box: Optional[Any] = None
        self.press_coord: Tuple[int, int] = (0, 0)
        self.move_coord: Tuple[int, int] = (0, 0)
        self.displayed_image: Optional[PhotoImage] = None
        self.canvas_image: Optional[Any] = None
        self.canvas_image_dimensions: Tuple[int, int] = (0, 0)
        self.current_image: Optional[Image] = None
        self.enabled_selection_mode: bool = False
        self.box_selected: bool = False
        self.current_file: int = 0
