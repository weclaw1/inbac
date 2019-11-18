import itertools
import tkinter as tk
import os

from tkinter import filedialog

from PIL import Image, ImageTk

import inbac.parse_arguments as args
import inbac.model as model
import inbac.view as view
import inbac.controller as controller

class Application():
    def __init__(self, args, master):
        self.model = model.Model(args)
        self.view = view.View(master, args.window_size)

        if args.input_dir is None:
            args.input_dir = filedialog.askdirectory(parent = master)
        args.output_dir = getattr(args, "output_dir", os.path.join(args.input_dir, "crops"))

        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)

        self.controller = controller.Controller(self.model, self.view)
        self.view.controller = self.controller

    def display_image_on_canvas(self, image):
        self.clear_canvas(self.image_canvas)
        self.current_image = image
        width = self.current_image.size[0]
        height = self.current_image.size[1]
        if width > self.image_canvas.winfo_width() or height > self.image_canvas.winfo_height():
            width_ratio = float(
                self.image_canvas.winfo_width()) / float(width)
            height_ratio = float(
                self.image_canvas.winfo_height()) / float(height)
            ratio = min(width_ratio, height_ratio)
            width = int(float(width) * float(ratio))
            height = int(float(height) * float(ratio))

        self.displayed_image = self.current_image.copy()
        self.displayed_image.thumbnail(
            (width, height), Image.ANTIALIAS)
        self.displayed_image = ImageTk.PhotoImage(self.displayed_image)
        self.canvas_image = self.image_canvas.create_image(
            0, 0, anchor=tk.NW, image=self.displayed_image)

    def enable_selection_mode(self, event=None):
        self.enabled_selection_mode = True

    def disable_selection_mode(self, event=None):
        self.enabled_selection_mode = False

    def clear_canvas(self, widget):
        self.clear_selection_box(widget)
        if self.canvas_image is not None:
            widget.delete(self.canvas_image)
            self.canvas_image = None

    def on_resize(self, event=None):
        self.display_image_on_canvas(self.current_image)

    def save_next(self, event=None):
        # check if image was selected then go to the next
        if self.save():
            self.next_image()

    def save(self, event=None):
        if self.selection_box is None:
            return False
        selected_box = self.image_canvas.coords(self.selection_box)
        displayed_image_size = (
            self.displayed_image.width(), self.displayed_image.height())
        box = self.get_real_box(
            selected_box, self.current_image.size, displayed_image_size)
        new_filename = self.find_available_name(
            self.args.output_dir, self.images[self.current_file])
        saved_image = self.current_image.copy().crop(box)
        if self.args.resize:
            saved_image = saved_image.resize(
                (self.args.resize[0], self.args.resize[1]), Image.LANCZOS)
        if self.args.image_format:
            new_filename, _ = os.path.splitext(new_filename)
        saved_image.save(os.path.join(self.args.output_dir, new_filename),
                         self.args.image_format, quality=self.args.image_quality)
        self.clear_selection_box(self.image_canvas)
        return True

    def next_image(self, event=None):
        if self.current_file + 1 >= len(self.images):
            return
        self.current_file += 1
        try:
            self.load_image(self.images[self.current_file])
        except IOError:
            self.next_image()

    def previous_image(self, event=None):
        if self.current_file - 1 < 0:
            return
        self.current_file -= 1
        try:
            self.load_image(self.images[self.current_file])
        except IOError:
            self.previous_image()

    def on_mouse_down(self, event):
        self.mouse_press_coord = (event.x, event.y)
        self.mouse_move_coord = (event.x, event.y)
        if self.enabled_selection_mode and self.selection_box is not None:
            selected_box = event.widget.coords(self.selection_box)
            self.box_selected = self.coordinates_in_selection_box(self.mouse_press_coord, selected_box)
        else:
            self.clear_selection_box(event.widget)

    def on_mouse_drag(self, event):
        if self.enabled_selection_mode and not self.box_selected:
            return
        prev_mouse_move_coord = self.mouse_move_coord
        self.mouse_move_coord = (event.x, event.y)
        if self.box_selected:
            x_delta = self.mouse_move_coord[0] - prev_mouse_move_coord[0]
            y_delta = self.mouse_move_coord[1] - prev_mouse_move_coord[1]
            event.widget.move(self.selection_box, x_delta, y_delta)
        else:
            self.update_selection_box(event.widget)

    def on_mouse_up(self, event):
        self.box_selected = False

    def clear_selection_box(self, widget):
        if self.selection_box is not None:
            widget.delete(self.selection_box)
            self.selection_box = None

    def update_selection_box(self, widget):
        selected_box = self.get_selected_box(
            self.mouse_press_coord, self.mouse_move_coord, self.args.aspect_ratio)

        if self.selection_box is None:
            self.selection_box = widget.create_rectangle(
                selected_box, outline=self.args.selection_box_color)
        else:
            widget.coords(self.selection_box, selected_box)

    @staticmethod
    def get_real_box(selected_box, original_image_size, displayed_image_size):
        return (int(selected_box[0] * original_image_size[0]/displayed_image_size[0]),
                int(selected_box[1] * original_image_size[1] /
                    displayed_image_size[1]),
                int(selected_box[2] * original_image_size[0] /
                    displayed_image_size[0]),
                int(selected_box[3] * original_image_size[1]/displayed_image_size[1]))

    @staticmethod
    def get_selected_box(mouse_press_coord, mouse_move_coord, aspect_ratio):
        selection_top_left_x = min(mouse_press_coord[0], mouse_move_coord[0])
        selection_top_left_y = min(mouse_press_coord[1], mouse_move_coord[1])
        selection_bottom_right_x = max(
            mouse_press_coord[0], mouse_move_coord[0])
        selection_bottom_right_y = max(
            mouse_press_coord[1], mouse_move_coord[1])
        selection_box = (selection_top_left_x, selection_top_left_y,
                         selection_bottom_right_x, selection_bottom_right_y)

        if aspect_ratio is not None:
            aspect_ratio = float(aspect_ratio[0])/float(aspect_ratio[1])
            try:
                selection_box = Application.get_selection_box_for_aspect_ratio(selection_box, aspect_ratio,
                                                                               mouse_press_coord, mouse_move_coord)
            except ZeroDivisionError:
                pass

        return tuple((lambda x: int(round(x)))(x) for x in selection_box)

    @staticmethod
    def get_selection_box_for_aspect_ratio(selection_box, aspect_ratio, mouse_press_coord, mouse_move_coord):
        selection_box = list(selection_box)
        width = selection_box[2] - selection_box[0]
        height = selection_box[3] - selection_box[1]
        if float(width)/float(height) > aspect_ratio:
            height = width / aspect_ratio
            if mouse_move_coord[1] > mouse_press_coord[1]:
                selection_box[3] = selection_box[1] + height
            else:
                selection_box[1] = selection_box[3] - height
        else:
            width = height * aspect_ratio
            if mouse_move_coord[0] > mouse_press_coord[0]:
                selection_box[2] = selection_box[0] + width
            else:
                selection_box[0] = selection_box[2] - width
        return tuple(selection_box)

    @staticmethod
    def find_available_name(directory, filename):
        name, extension = os.path.splitext(filename)
        if not os.path.isfile(os.path.join(directory, filename)):
            return filename
        for num in itertools.count(2):
            if not os.path.isfile(os.path.join(directory, name + str(num) + extension)):
                return name + str(num) + extension

    @staticmethod
    def coordinates_in_selection_box(coordinates, selection_box):
        if (coordinates[0] > selection_box[0] and coordinates[0] < selection_box[2] 
        and coordinates[1] > selection_box[1] and coordinates[1] < selection_box[3]):
            return True
        else:
            return False


def main():
    root = tk.Tk()
    app = Application(args.parse_arguments(), master=root)

    app.master.mainloop()


if __name__ == "__main__":
    main()
