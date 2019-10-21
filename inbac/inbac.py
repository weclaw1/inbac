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
            self.input_dir = sys.argv[1]
        else:
            self.input_dir = os.getcwd()
        self.files = self.load_images(self.input_dir)
        self.output_dir = os.path.join(self.input_dir, output_directory)

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.selection_box = None

        self.mouse_press_coord = (0, 0)
        self.mouse_move_coord = (0, 0)

        self.image_canvas = tk.Canvas(self, highlightthickness=0)
        self.image_canvas.pack(fill=tk.BOTH, expand=tk.YES)

        self.master.bind('z', self.save_next)
        self.master.bind('x', self.save)
        self.master.bind('<Left>', self.previous_image)
        self.master.bind('<Right>', self.next_image)
        self.master.bind('<ButtonPress-1>', self.on_mouse_down)
        self.master.bind('<B1-Motion>', self.on_mouse_drag)

        self.current_file = 0

        self.load_image_from_file(self.files[self.current_file], True)

    def load_image_from_file(self, filename, first_image):
        self.image_canvas.delete("all")
        self.current_filename = filename
        self.original_image = Image.open(os.path.join(self.input_dir, filename))
        if first_image:
            self.width = 800
        else:
            self.width = self.master.winfo_width()
        width_percent = self.width/float(self.original_image.size[0])
        self.height = int(float(self.original_image.size[1]) * float(width_percent))
        self.master.geometry(str(self.width) + "x" + str(self.height))
        self.displayed_image = self.original_image.copy()
        self.displayed_image.thumbnail((self.width, self.height), Image.NEAREST)
        self.displayed_image = ImageTk.PhotoImage(self.displayed_image)
        self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.displayed_image)

    def save_next(self, event=None):
        self.save()
        self.next_image()

    def save(self, event=None):
        box = self.get_selected_box()
        new_filename = self.find_available_name(self.output_dir, self.current_filename)
        subprocess.run(
            ["convert", os.path.join(self.input_dir, self.current_filename),
             "-crop", str(box[2] - box[0]) + "x" + str(box[3] - box[1]) + "+" + str(box[0]) + "+" + str(box[1]),
             "-resize", str(resize_width) + "x" + str(resize_height),
             ">", os.path.join(self.output_dir, new_filename)], shell=True)

    def next_image(self, event=None):
        if self.current_file + 1 >= len(self.files):
            return
        self.current_file += 1
        self.load_image_from_file(self.files[self.current_file], False)

    def previous_image(self, event=None):
        if self.current_file - 1 < 0:
            return
        self.current_file -= 1
        self.load_image_from_file(self.files[self.current_file], False)

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
        return (selected_box[0] * self.original_image.size[0]/self.displayed_image.width(),
                selected_box[1] * self.original_image.size[1]/self.displayed_image.height(),
                selected_box[2] * self.original_image.size[0]/self.displayed_image.width(),
                selected_box[3] * self.original_image.size[1]/self.displayed_image.height())

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
        
        return tuple(lambda x: int(round(x)) for x in selection_box)

    def get_selection_box_for_aspect_ratio(self, selection_box, aspect_ratio):
        width = selection_box[2] - selection_box[0]
        height = selection_box[3] - selection_box[1]
        if float(width)/float(height) > aspect_ratio:
            height = width / aspect_ratio
            if self.mouse_move_coord[1] > self.mouse_press_coord[1]:
                selection_box[4] = selection_box[1] + height
            else:
                selection_box[1] = selection_box[4] - height
        else:
            width = height * aspect_ratio
            if self.mouse_move_coord[0] > self.mouse_press_coord[0]:
                selection_box[2] = selection_box[0] + width
            else:
                selection_box[0] = selection_box[2] - width
        return selection_box

    @staticmethod
    def load_images(dir):
        all_images = []
        for filename in os.listdir(dir):
            _, extension = os.path.splitext(filename)
            if extension.lower() not in image_extensions: continue
            all_images.append(filename)
        return all_images

    @staticmethod
    def find_available_name(dir, filename):
        if os.path.isfile(os.path.join(dir, filename)):
            return filename
        for num in itertools.count(2):
            if os.path.isfile(os.path.join(dir, filename + str(num))):
                return filename + str(num)


root = tk.Tk()
app = Application(master=root)
app.master.title("inbac")

app.mainloop()