import itertools
import mimetypes
import os

from typing import Optional, List, Tuple

from PIL import Image, ImageTk

from inbac.model import Model
from inbac.view import View


class Controller():
    def __init__(self, model: Model, view: View):
        self.model: Model = model
        self.view: View = view

        self.load_images()

    def select_images_folder(self):
        input_dir = self.view.ask_directory()
        if input_dir:
            self.model.args.input_dir = input_dir
            self.model.args.output_dir = os.path.join(
                self.model.args.input_dir, "crops")

            if not os.path.exists(self.model.args.output_dir):
                self.create_output_directory()

    def create_output_directory(self):
        try:
            os.makedirs(self.model.args.output_dir)
        except OSError:
            self.view.show_error(
                "Error", "Output directory cannot be created, please select output directory location")
            self.model.args.output_dir = self.view.ask_directory()

    def load_image(self, image_name: str):
        if self.model.current_image is not None:
            self.model.current_image.close()
            self.model.current_image = None
        image = Image.open(os.path.join(self.model.args.input_dir, image_name))
        self.display_image_on_canvas(image)
        self.view.set_title(image_name)

    def load_images(self):
        if self.model.args.input_dir:
            try:
                self.model.images = self.load_image_list(
                    self.model.args.input_dir)
            except OSError:
                self.view.show_error(
                    "Error", "Input directory cannot be opened")

        if self.model.images:
            try:
                self.model.current_file = 0
                self.load_image(self.model.images[self.model.current_file])
            except IOError:
                self.next_image()

    def display_image_on_canvas(self, image: Image):
        self.clear_canvas()
        self.model.current_image = image
        self.model.canvas_image_dimensions = self.calculate_canvas_image_dimensions(self.model.current_image.size[0],
                                                                                    self.model.current_image.size[1],
                                                                                    self.view.image_canvas.winfo_width(),
                                                                                    self.view.image_canvas.winfo_height())
        displayed_image: Image = self.model.current_image.copy()
        displayed_image.thumbnail(
            self.model.canvas_image_dimensions, Image.ANTIALIAS)
        self.model.displayed_image = ImageTk.PhotoImage(displayed_image)
        self.model.canvas_image = self.view.display_image(
            self.model.displayed_image)

    def clear_canvas(self):
        self.clear_selection_box()
        if self.model.canvas_image is not None:
            self.view.remove_from_canvas(self.model.canvas_image)
            self.model.canvas_image = None

    def clear_selection_box(self):
        if self.model.selection_box is not None:
            self.view.remove_from_canvas(self.model.selection_box)
            self.model.selection_box = None

    def update_selection_box(self):
        selected_box: Tuple[int, int, int, int] = self.get_selected_box(
            self.model.press_coord, self.model.move_coord, self.model.args.aspect_ratio)

        if self.model.selection_box is None:
            self.model.selection_box = self.view.create_rectangle(
                selected_box, self.model.args.selection_box_color)
        else:
            self.view.change_canvas_object_coords(
                self.model.selection_box, selected_box)

    def stop_selection(self):
        self.model.box_selected = False

    def start_selection(self, press_coord: Tuple[int, int]):
        self.model.press_coord = press_coord
        self.model.move_coord = press_coord
        if self.model.enabled_selection_mode and self.model.selection_box is not None:
            selected_box: Tuple[int, int, int, int] = self.view.get_canvas_object_coords(
                self.model.selection_box)
            self.model.box_selected = self.coordinates_in_selection_box(
                self.model.press_coord, selected_box)
        else:
            self.clear_selection_box()

    def move_selection(self, move_coord: Tuple[int, int]):
        if self.model.enabled_selection_mode and not self.model.box_selected:
            return
        prev_move_coord: Tuple[int, int] = self.model.move_coord
        self.model.move_coord = move_coord
        if self.model.box_selected:
            x_delta: int = self.model.move_coord[0] - prev_move_coord[0]
            y_delta: int = self.model.move_coord[1] - prev_move_coord[1]
            self.view.move_canvas_object_by_offset(
                self.model.selection_box, x_delta, y_delta)
        else:
            self.update_selection_box()

    def next_image(self):
        if self.model.current_file + 1 >= len(self.model.images):
            return
        self.model.current_file += 1
        try:
            self.load_image(self.model.images[self.model.current_file])
        except IOError:
            self.next_image()

    def previous_image(self):
        if self.model.current_file - 1 < 0:
            return
        self.model.current_file -= 1
        try:
            self.load_image(self.model.images[self.model.current_file])
        except IOError:
            self.previous_image()

    def save_next(self):
        if self.save():
            self.next_image()

    def save(self) -> bool:
        if self.model.selection_box is None:
            return False
        selected_box: Tuple[int, int, int, int] = self.view.get_canvas_object_coords(
            self.model.selection_box)
        box: Tuple[int, int, int, int] = self.get_real_box(
            selected_box, self.model.current_image.size, self.model.canvas_image_dimensions)
        new_filename: str = self.find_available_name(
            self.model.args.output_dir, self.model.images[self.model.current_file])
        saved_image: Image = self.model.current_image.copy().crop(box)
        if self.model.args.resize:
            saved_image = saved_image.resize(
                (self.model.args.resize[0], self.model.args.resize[1]), Image.LANCZOS)
        if self.model.args.image_format:
            new_filename, _ = os.path.splitext(new_filename)
        saved_image.save(os.path.join(self.model.args.output_dir, new_filename),
                         self.model.args.image_format, quality=self.model.args.image_quality)
        self.clear_selection_box()
        return True

    @staticmethod
    def calculate_canvas_image_dimensions(image_width: int,
                                          image_height: int,
                                          canvas_width: int,
                                          canvas_height: int) -> Tuple[int, int]:
        if image_width > canvas_width or image_height > canvas_height:
            width_ratio: float = canvas_width / image_width
            height_ratio: float = canvas_height / image_height
            ratio: float = min(width_ratio, height_ratio)
            new_image_width: int = int(image_width * ratio)
            new_image_height: int = int(image_height * ratio)
            return (new_image_width, new_image_height)
        return (image_width, image_height)

    @staticmethod
    def load_image_list(directory: str) -> List[str]:
        images: List[str] = []

        for filename in os.listdir(directory):
            filetype, _ = mimetypes.guess_type(filename)
            if filetype is None or filetype.split("/")[0] != "image":
                continue
            images.append(filename)

        return images

    @staticmethod
    def coordinates_in_selection_box(coordinates: Tuple[int, int], selection_box: Tuple[int, int]) -> bool:
        return (coordinates[0] > selection_box[0] and coordinates[0] < selection_box[2]
                and coordinates[1] > selection_box[1] and coordinates[1] < selection_box[3])

    @staticmethod
    def find_available_name(directory: str, filename: str) -> str:
        name, extension = os.path.splitext(filename)
        if not os.path.isfile(os.path.join(directory, filename)):
            return filename
        for num in itertools.count(2):
            if not os.path.isfile(os.path.join(directory, name + str(num) + extension)):
                return name + str(num) + extension

    @staticmethod
    def get_selection_box_for_aspect_ratio(selection_box: Tuple[int, int, int, int],
                                           aspect_ratio: float,
                                           mouse_press_coord: Tuple[int, int],
                                           mouse_move_coord: Tuple[int, int]) -> Tuple[int, int, int, int]:
        selection_box: List[int] = list(selection_box)
        width: int = selection_box[2] - selection_box[0]
        height: int = selection_box[3] - selection_box[1]
        if float(width)/float(height) > aspect_ratio:
            height = round(width / aspect_ratio)
            if mouse_move_coord[1] > mouse_press_coord[1]:
                selection_box[3] = selection_box[1] + height
            else:
                selection_box[1] = selection_box[3] - height
        else:
            width = round(height * aspect_ratio)
            if mouse_move_coord[0] > mouse_press_coord[0]:
                selection_box[2] = selection_box[0] + width
            else:
                selection_box[0] = selection_box[2] - width
        return tuple(selection_box)

    @staticmethod
    def get_selected_box(mouse_press_coord: Tuple[int, int], mouse_move_coord: Tuple[int, int],
                         aspect_ratio: Optional[Tuple[int, int]]) -> Tuple[int, int, int, int]:
        selection_top_left_x: int = min(
            mouse_press_coord[0], mouse_move_coord[0])
        selection_top_left_y: int = min(
            mouse_press_coord[1], mouse_move_coord[1])
        selection_bottom_right_x: int = max(
            mouse_press_coord[0], mouse_move_coord[0])
        selection_bottom_right_y: int = max(
            mouse_press_coord[1], mouse_move_coord[1])
        selection_box: Tuple[int, int, int, int] = (selection_top_left_x, selection_top_left_y,
                                                    selection_bottom_right_x, selection_bottom_right_y)

        if aspect_ratio is not None:
            aspect_ratio: float = float(aspect_ratio[0])/float(aspect_ratio[1])
            try:
                selection_box: Tuple[int, int, int, int] = Controller.get_selection_box_for_aspect_ratio(selection_box, aspect_ratio,
                                                                                                         mouse_press_coord, mouse_move_coord)
            except ZeroDivisionError:
                pass

        return selection_box

    @staticmethod
    def get_real_box(selected_box: Tuple[int, int, int, int], original_image_size: Tuple[int, int],
                     displayed_image_size: Tuple[int, int]) -> Tuple[int, int, int, int]:
        return (int(selected_box[0] * original_image_size[0]/displayed_image_size[0]),
                int(selected_box[1] * original_image_size[1] /
                    displayed_image_size[1]),
                int(selected_box[2] * original_image_size[0] /
                    displayed_image_size[0]),
                int(selected_box[3] * original_image_size[1]/displayed_image_size[1]))
