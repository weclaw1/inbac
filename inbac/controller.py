import mimetypes
import os
from tkinter import filedialog

from PIL import Image, ImageTk

class Controller():
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.model.images = self.load_image_list(self.model.args.input_dir)
        self.load_image(self.model.images[self.model.current_file])

    def load_image(self, image_name):
        if self.model.current_image is not None:
            self.model.current_image.close()
            self.model.current_image = None
        image = Image.open(os.path.join(self.model.args.input_dir, image_name))
        self.display_image_on_canvas(image)
        self.view.set_title(image_name)

    @staticmethod
    def load_image_list(directory):
        images = []

        for filename in os.listdir(directory):
            filetype, _ = mimetypes.guess_type(filename)
            if filetype is None or filetype.split("/")[0] != "image":
                continue
            images.append(filename)

        return images