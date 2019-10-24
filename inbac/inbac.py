import sys
import os
import itertools
import tkinter as tk
import subprocess
from PIL import Image, ImageTk

image_extensions = [".jpg", ".jpeg", ".png", ".bmp"]

output_directory = "crops"

resize_width = 256
resize_height = 256

fixed_aspect_ratio = True
aspect_ratio_x = 1
aspect_ratio_y = 1

selection_box_color = "black"

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=tk.YES)

        if len(sys.argv) > 1:
            self.input_directory = sys.argv[1]
        else:
            self.input_directory = os.getcwd()

        self.files = self.load_images(self.input_directory)

        output_directory_path = os.path.join(self.input_directory, output_directory)
        if not os.path.exists(output_directory_path):
            os.makedirs(output_directory_path)

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
        self.master.bind('<ButtonPress-1>', self.on_mouse_down)
        self.master.bind('<B1-Motion>', self.on_mouse_drag)

        self.current_file = 0
        
        self.master.geometry("800x600")
        self.master.update()
        self.load_image_from_file(self.files[self.current_file])

    def load_image_from_file(self, filename):
        self.clear_canvas(self.image_canvas)
        
        self.original_image = Image.open(os.path.join(self.input_directory, filename))
        self.width = self.original_image.size[0]
        self.height = self.original_image.size[1]
        if self.width > self.master.winfo_width() or self.height > self.master.winfo_height():
            width_ratio = float(self.master.winfo_width()) / self.width
            height_ratio = float(self.master.winfo_height()) / self.height
            ratio = min(width_ratio, height_ratio)
            self.width = int(float(self.width) * float(ratio))
            self.height = int(float(self.height) * float(ratio))

        self.displayed_image = self.original_image.copy()
        self.displayed_image.thumbnail((self.width, self.height), Image.ANTIALIAS)
        self.displayed_image = ImageTk.PhotoImage(self.displayed_image)
        self.canvas_image = self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.displayed_image)

    def clear_canvas(self, widget):
        self.clear_selection_box(widget)
        if self.canvas_image is not None:
            widget.delete(self.canvas_image)
            self.canvas_image = None

    def save_next(self, event=None):
        self.save()
        self.next_image()

    def save(self, event=None):
        if self.selection_box is None:
            return
        filename = self.files[self.current_file]
        output_directory_path = os.path.join(self.input_directory, output_directory)
        box = self.get_real_box(self.get_selected_box())
        new_filename = self.find_available_name(output_directory_path, filename)
        subprocess.run(["convert", os.path.join(self.input_directory, filename),
                        "-crop", str(box[2] - box[0]) + "x" + str(box[3] - box[1]) + "+" + str(box[0]) + "+" + str(box[1]),
                        "-resize", str(resize_width) + "x" + str(resize_height),
                        os.path.join(output_directory_path, new_filename)])
        self.clear_selection_box(self.image_canvas)

    def next_image(self, event=None):
        if self.current_file + 1 >= len(self.files):
            return
        self.current_file += 1
        self.load_image_from_file(self.files[self.current_file])

    def previous_image(self, event=None):
        if self.current_file - 1 < 0:
            return
        self.current_file -= 1
        self.load_image_from_file(self.files[self.current_file])

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
        selected_box = self.get_selected_box()

        if self.selection_box is None:
            self.selection_box = widget.create_rectangle(selected_box, outline=selection_box_color)
        else:
            widget.coords(self.selection_box, selected_box)
        
    def get_real_box(self, selected_box):
        return (int(selected_box[0] * self.original_image.size[0]/self.displayed_image.width()),
                int(selected_box[1] * self.original_image.size[1]/self.displayed_image.height()),
                int(selected_box[2] * self.original_image.size[0]/self.displayed_image.width()),
                int(selected_box[3] * self.original_image.size[1]/self.displayed_image.height()))

    def get_selected_box(self):
        selection_top_left_x = min(self.mouse_press_coord[0], self.mouse_move_coord[0])
        selection_top_left_y = min(self.mouse_press_coord[1], self.mouse_move_coord[1])
        selection_bottom_right_x = max(self.mouse_press_coord[0], self.mouse_move_coord[0])
        selection_bottom_right_y = max(self.mouse_press_coord[1], self.mouse_move_coord[1])
        selection_box = (selection_top_left_x, selection_top_left_y, selection_bottom_right_x, selection_bottom_right_y)
        width = selection_bottom_right_x - selection_top_left_x
        height = selection_bottom_right_y - selection_top_left_y

        if fixed_aspect_ratio:
            aspect_ratio = float(aspect_ratio_x)/float(aspect_ratio_y)
            selection_box = self.get_selection_box_for_aspect_ratio(selection_box, aspect_ratio)
        
        return tuple((lambda x: int(round(x)))(x) for x in selection_box)

    def get_selection_box_for_aspect_ratio(self, selection_box, aspect_ratio):
        selection_box = list(selection_box)
        width = selection_box[2] - selection_box[0]
        height = selection_box[3] - selection_box[1]
        try:
            if float(width)/float(height) > aspect_ratio:
                height = width / aspect_ratio
                if self.mouse_move_coord[1] > self.mouse_press_coord[1]:
                    selection_box[3] = selection_box[1] + height
                else:
                    selection_box[1] = selection_box[3] - height
            else:
                width = height * aspect_ratio
                if self.mouse_move_coord[0] > self.mouse_press_coord[0]:
                    selection_box[2] = selection_box[0] + width
                else:
                    selection_box[0] = selection_box[2] - width
        except ZeroDivisionError:
            pass
        return tuple(selection_box)

    @staticmethod
    def load_images(directory):
        all_images = []
        for filename in os.listdir(directory):
            _, extension = os.path.splitext(filename)
            if extension.lower() not in image_extensions: continue
            all_images.append(filename)
        return all_images

    @staticmethod
    def find_available_name(directory, filename):
        name, extension = os.path.splitext(filename)
        if not os.path.isfile(os.path.join(directory, filename)):
            return filename
        for num in itertools.count(2):
            if not os.path.isfile(os.path.join(directory, name + str(num) + extension)):
                return name + str(num) + extension


root = tk.Tk()
app = Application(master=root)
app.master.title("inbac")

app.mainloop()