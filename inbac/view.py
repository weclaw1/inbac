import tkinter as tk
from tkinter import Tk, Frame, Canvas, Event, Menu, messagebox
from typing import Optional, List, Tuple, Any
from PIL.ImageTk import PhotoImage
import inbac

class View():
    def __init__(self, master: Tk, initial_window_size: Tuple[int, int]):
        self.master: Tk = master
        self.frame: Frame = tk.Frame(self.master, relief=tk.FLAT)
        self.frame.pack(fill=tk.BOTH, expand=tk.YES)
        self.image_canvas: Canvas = Canvas(self.frame, highlightthickness=0)
        self.image_canvas.pack(fill=tk.BOTH, expand=tk.YES)
        self.master.geometry(str(initial_window_size[0]) + "x" + str(initial_window_size[1]))
        self.master.update()
        self.controller = None

        self.bind_events()
        self.create_menu()

    def bind_events(self):
        self.master.bind('z', self.save_next)
        self.master.bind('x', self.save)
        self.master.bind('<Left>', self.previous_image)
        self.master.bind('<Right>', self.next_image)
        self.master.bind('<ButtonPress-3>', self.next_image)
        self.master.bind('<ButtonPress-2>', self.previous_image)
        self.image_canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.image_canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.image_canvas.bind('<ButtonRelease-1>', self.on_mouse_up)

        self.master.bind('<KeyPress-Shift_L>', self.enable_selection_mode)
        self.master.bind('<KeyPress-Control_L>', self.enable_selection_mode)
        self.master.bind('<KeyRelease-Shift_L>', self.disable_selection_mode)
        self.master.bind('<KeyRelease-Control_L>', self.disable_selection_mode)

        self.image_canvas.bind('<Configure>', self.on_resize)

    def create_menu(self):
        self.menu: Menu = Menu(self.master, relief=tk.FLAT)
        self.menu.add_command(label="Open", command=self.open_dialog)
        self.menu.add_command(label="Settings", command=self.create_settings_window)
        self.menu.add_command(label="About", command=self.show_about_dialog)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.master.quit)
        self.master.config(menu=self.menu)

    def open_dialog(self):
        pass

    def create_settings_window(self):
        pass

    def show_about_dialog(self):
        messagebox.showinfo("About", "inbac " + inbac.__version__, parent = self.master)
    
    def show_error(self, title: str, message: str):
        messagebox.showerror(title, message, parent=self.master)

    def display_image(self, image: PhotoImage) -> Any:
        return self.image_canvas.create_image(0, 0, anchor=tk.NW, image=image)

    def remove_from_canvas(self, obj: Any):
        self.image_canvas.delete(obj)

    def create_rectangle(self, box: Tuple[int, int, int, int], outline_color: str) -> Any:
        return self.image_canvas.create_rectangle(box, outline=outline_color)

    def change_canvas_object_coords(self, obj: Any, coords: Tuple[int, int]):
        self.image_canvas.coords(obj, coords)

    def get_canvas_object_coords(self, obj: Any) -> Any:
        return self.image_canvas.coords(obj)

    def move_canvas_object_by_offset(self, obj: Any, offset_x: int, offset_y: int):
        self.image_canvas.move(obj, offset_x, offset_y)

    def enable_selection_mode(self, event: Event = None):
        self.controller.model.enabled_selection_mode = True

    def disable_selection_mode(self, event: Event = None):
        self.controller.model.enabled_selection_mode = False

    def on_mouse_down(self, event: Event):
        self.controller.start_selection((event.x, event.y))

    def on_mouse_drag(self, event: Event):
        self.controller.move_selection((event.x, event.y))

    def on_mouse_up(self, event: Event):
        self.controller.stop_selection()

    def next_image(self, event: Event = None):
        self.controller.next_image()

    def previous_image(self, event: Event = None):
        self.controller.previous_image()

    def on_resize(self, event: Event = None):
        self.controller.display_image_on_canvas(self.controller.model.current_image)

    def save_next(self, event: Event = None):
        self.controller.save_next()

    def save(self, event: Event = None):
        self.controller.save()

    def set_title(self, title: str):
        self.master.title(title)