import tkinter as tk
import types
from tkinter import Tk, Frame, Canvas, Event, Menu, messagebox, filedialog, Toplevel
from typing import Tuple, Any
from PIL.ImageTk import PhotoImage
import inbac


class View():
    def __init__(self, master: Tk, initial_window_size: Tuple[int, int]):
        self.master: Tk = master
        self.frame: Frame = tk.Frame(self.master, relief=tk.FLAT)
        self.frame.pack(fill=tk.BOTH, expand=tk.YES)
        self.image_canvas: Canvas = Canvas(self.frame, highlightthickness=0)
        self.image_canvas.pack(fill=tk.BOTH, expand=tk.YES)
        self.master.geometry(
            str(initial_window_size[0]) + "x" + str(initial_window_size[1]))
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
        self.menu.add_command(
            label="Settings", command=self.create_settings_window)
        self.menu.add_command(label="About", command=self.show_about_dialog)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.master.quit)
        self.master.config(menu=self.menu)

    def ask_directory(self) -> str:
        return filedialog.askdirectory(parent=self.master)

    def open_dialog(self):
        self.controller.select_images_folder()
        self.controller.load_images()

    def create_settings_window(self):
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Settings")
        settings_window.geometry("{}x{}".format(400, 400))
        settings = types.SimpleNamespace()

        settings.aspect_ratio_checked = tk.IntVar()
        settings.aspect_ratio_checked.set(
            self.controller.model.args.aspect_ratio is not None)
        aspect_ratio_checkbox = tk.Checkbutton(
            settings_window, variable=settings.aspect_ratio_checked, onvalue=1, offvalue=0, text="Aspect Ratio")
        aspect_ratio_checkbox.grid(row=0, column=0, columnspan=2, sticky=tk.W)

        settings.aspect_ratio_x = tk.StringVar()
        if self.controller.model.args.aspect_ratio is not None:
            settings.aspect_ratio_x.set(
                str(self.controller.model.args.aspect_ratio[0]))
        aspect_ratio_x_entry = tk.Entry(
            settings_window, width=5, textvariable=settings.aspect_ratio_x, bg="white")
        aspect_ratio_x_entry.grid(row=1, column=0)

        settings.aspect_ratio_y = tk.StringVar()
        if self.controller.model.args.aspect_ratio is not None:
            settings.aspect_ratio_y.set(
                str(self.controller.model.args.aspect_ratio[1]))
        aspect_ratio_y_entry = tk.Entry(
            settings_window, width=5, textvariable=settings.aspect_ratio_y, bg="white")
        aspect_ratio_y_entry.grid(row=1, column=1)

        settings.resize_checked = tk.IntVar()
        settings.resize_checked.set(
            self.controller.model.args.resize is not None)
        resize_checkbox = tk.Checkbutton(
            settings_window, variable=settings.resize_checked, onvalue=1, offvalue=0, text="Resize")
        resize_checkbox.grid(row=2, column=0, columnspan=2, sticky=tk.W)

        settings.resize_x = tk.StringVar()
        if self.controller.model.args.resize is not None:
            settings.resize_x.set(str(self.controller.model.args.resize[0]))
        resize_x_entry = tk.Entry(
            settings_window, width=5, textvariable=settings.resize_x, bg="white")
        resize_x_entry.grid(row=3, column=0)

        settings.resize_y = tk.StringVar()
        if self.controller.model.args.resize is not None:
            settings.resize_y.set(str(self.controller.model.args.resize[1]))
        resize_y_entry = tk.Entry(
            settings_window, width=5, textvariable=settings.resize_y, bg="white")
        resize_y_entry.grid(row=3, column=1)

        save_button = tk.Button(settings_window, text="Save",
                                command=lambda: self.save_settings(settings_window, settings))
        save_button.grid(row=4, column=0)

        cancel_button = tk.Button(settings_window, text="Cancel",
                                  command=lambda: self.cancel_settings(settings_window))
        cancel_button.grid(row=4, column=1)

    def save_settings(self, settings_window: Toplevel, settings: types.SimpleNamespace):
        if settings.aspect_ratio_checked.get():
            self.controller.model.args.aspect_ratio = (
                int(settings.aspect_ratio_x.get()), int(settings.aspect_ratio_y.get()))
        else:
            self.controller.model.args.aspect_ratio = None
        if settings.resize_checked.get():
            self.controller.model.args.resize = (
                int(settings.resize_x.get()), int(settings.resize_y.get()))
        else:
            self.controller.model.args.resize = None
        settings_window.destroy()

    def cancel_settings(self, settings_window: Toplevel):
        settings_window.destroy()

    def show_about_dialog(self):
        messagebox.showinfo("About", "inbac " +
                            inbac.__version__, parent=self.master)

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
        self.controller.display_image_on_canvas(
            self.controller.model.current_image)

    def save_next(self, event: Event = None):
        self.controller.save_next()

    def save(self, event: Event = None):
        self.controller.save()

    def set_title(self, title: str):
        self.master.title(title)
