import itertools
import mimetypes
import os
import subprocess
import sys
import tkinter as tk

from PIL import Image, ImageTk

import inbac.parse_arguments as args


class Application(tk.Frame):
    def __init__(self, args, master=None):
        super().__init__(master)
        self.master = master
        self.args = args
        self.pack(fill=tk.BOTH, expand=tk.YES)

        self.images = self.load_images(
            self.args.input_dir, self.args.preload_images)

        if not os.path.exists(self.args.output_dir):
            os.makedirs(self.args.output_dir)

        self.selection_box = None

        self.mouse_press_coord = (0, 0)
        self.mouse_move_coord = (0, 0)

        self.image_canvas = tk.Canvas(self, highlightthickness=0)
        self.image_canvas.pack(fill=tk.BOTH, expand=tk.YES)

        self.canvas_image = None

        self.master.bind('z', self.save_next)
        self.master.bind('x', self.save)
        self.master.bind('<Left>', self.previous_image)
        self.master.bind('<Right>', self.next_image)
        self.master.bind('<ButtonPress-3>', self.next_image)
        self.master.bind('<ButtonPress-2>', self.previous_image)
        self.master.bind('<ButtonPress-1>', self.on_mouse_down)
        self.master.bind('<B1-Motion>', self.on_mouse_drag)

        self.current_file = 0

        self.master.geometry(
            str(self.args.window_size[0]) + "x" + str(self.args.window_size[1]))
        self.master.update()
        self.display_image_on_canvas(self.images[self.current_file])
        self.image_canvas.bind('<Configure>', self.on_resize)
        self.update_window_title()

    def display_image_on_canvas(self, image):
        self.clear_canvas(self.image_canvas)
        self.width = image.size[0]
        self.height = image.size[1]
        if self.width > self.image_canvas.winfo_width() or self.height > self.image_canvas.winfo_height():
            width_ratio = float(
                self.image_canvas.winfo_width()) / float(self.width)
            height_ratio = float(
                self.image_canvas.winfo_height()) / float(self.height)
            ratio = min(width_ratio, height_ratio)
            self.width = int(float(self.width) * float(ratio))
            self.height = int(float(self.height) * float(ratio))

        self.displayed_image = image.copy()
        self.displayed_image.thumbnail(
            (self.width, self.height), Image.ANTIALIAS)
        self.displayed_image = ImageTk.PhotoImage(self.displayed_image)
        self.canvas_image = self.image_canvas.create_image(
            0, 0, anchor=tk.NW, image=self.displayed_image)

    def clear_canvas(self, widget):
        self.clear_selection_box(widget)
        if self.canvas_image is not None:
            widget.delete(self.canvas_image)
            self.canvas_image = None

    def on_resize(self, event=None):
        self.display_image_on_canvas(self.images[self.current_file])

    def save_next(self, event=None):
        self.save()
        self.next_image()

    def save(self, event=None):
        if self.selection_box is None:
            return
        filename = os.path.basename(self.images[self.current_file].filename)
        selected_box = self.get_selected_box(
            self.mouse_press_coord, self.mouse_move_coord, self.args.aspect_ratio)
        displayed_image_size = (
            self.displayed_image.width(), self.displayed_image.height())
        box = self.get_real_box(
            selected_box, self.images[self.current_file].size, displayed_image_size)
        new_filename = self.find_available_name(self.args.output_dir, filename)
        image = self.images[self.current_file].copy().crop(box)
        if self.args.resize:
            image = image.resize(
                (self.args.resize[0], self.args.resize[1]), Image.LANCZOS)
        image.save(os.path.join(self.args.output_dir, new_filename))
        self.clear_selection_box(self.image_canvas)

    def next_image(self, event=None):
        if self.current_file + 1 >= len(self.images):
            return
        self.current_file += 1
        self.display_image_on_canvas(self.images[self.current_file])
        self.update_window_title()

    def previous_image(self, event=None):
        if self.current_file - 1 < 0:
            return
        self.current_file -= 1
        self.display_image_on_canvas(self.images[self.current_file])
        self.update_window_title()

    def on_mouse_down(self, event):
        self.mouse_press_coord = (event.x, event.y)
        self.clear_selection_box(event.widget)

    def on_mouse_drag(self, event):
        self.mouse_move_coord = (event.x, event.y)
        self.update_selection_box(event.widget)

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

    def update_window_title(self):
        self.master.title(os.path.basename(
            self.images[self.current_file].filename))

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
    def load_images(directory, preload_images):
        images = []

        for filename in os.listdir(directory):
            filetype, _ = mimetypes.guess_type(filename)
            if filetype is None or filetype.split("/")[0] != "image":
                continue
            try:
                image = Image.open(os.path.join(directory, filename))
                if preload_images:
                    image.load()
                images.append(image)
            except IOError:
                pass

        return images

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


def main():
    root = tk.Tk()
    app = Application(args.parse_arguments(), master=root)

    app.mainloop()


if __name__ == "__main__":
    main()
