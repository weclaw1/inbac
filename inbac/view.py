import tkinter as tk

class View():
    def __init__(self, master, initial_window_size):
        self.master = master
        self.frame = tk.Frame(master, relief=tk.RIDGE, borderwidth=2)
        self.frame.pack(fill=tk.BOTH, expand=tk.YES)
        self.image_canvas = tk.Canvas(self.frame, highlightthickness=0)
        self.image_canvas.pack(fill=tk.BOTH, expand=tk.YES)
        self.master.geometry(str(initial_window_size[0]) + "x" + str(initial_window_size[1]))
        self.master.update()
        self.controller = None

        self._bind_events()

    def _bind_events(self):
        self.frame.bind('z', self.save_next)
        self.frame.bind('x', self.save)
        self.frame.bind('<Left>', self.previous_image)
        self.frame.bind('<Right>', self.next_image)
        self.frame.bind('<ButtonPress-3>', self.next_image)
        self.frame.bind('<ButtonPress-2>', self.previous_image)
        self.image_canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.image_canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.image_canvas.bind('<ButtonRelease-1>', self.on_mouse_up)

        self.frame.bind('<KeyPress-Shift_L>', self.enable_selection_mode)
        self.frame.bind('<KeyPress-Control_L>', self.enable_selection_mode)
        self.frame.bind('<KeyRelease-Shift_L>', self.disable_selection_mode)
        self.frame.bind('<KeyRelease-Control_L>', self.disable_selection_mode)

        self.image_canvas.bind('<Configure>', self.on_resize)

    def display_image(self, image):
        return self.image_canvas.create_image(0, 0, anchor=tk.NW, image=image)

    def remove_from_canvas(self, obj):
        self.image_canvas.delete(obj)

    def create_rectangle(self, box, outline_color):
        self.image_canvas.create_rectangle(box, outline=outline_color)

    def change_canvas_object_coords(self, obj, coords):
        self.image_canvas.coords(obj, coords)

    def get_canvas_object_coords(self, obj):
        return self.image_canvas.coords(obj)

    def move_canvas_object_by_offset(self, obj, offset_x, offset_y):
        self.image_canvas.move(object, offset_x, offset_y)

    def enable_selection_mode(self, event=None):
        self.controller.model.enabled_selection_mode = True

    def disable_selection_mode(self, event=None):
        self.controller.model.enabled_selection_mode = False

    def on_mouse_down(self, event):
        self.controller.start_selection((event.x, event.y))

    def on_mouse_drag(self, event):
        self.controller.move_selection((event.x, event.y))

    def on_mouse_up(self, event):
        self.controller.stop_selection()

    def next_image(self, event=None):
        self.controller.next_image()

    def previous_image(self, event=None):
        self.controller.previous_image()

    def on_resize(self, event=None):
        self.controller.display_image_on_canvas(self.controller.model.current_image)

    def save_next(self, event=None):
        self.controller.save_next()

    def save(self, event=None):
        self.controller.save()

    def set_title(self, title):
        self.master.title(title)