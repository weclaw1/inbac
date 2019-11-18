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
        self.master.bind('z', self.save_next)
        self.master.bind('x', self.save)
        self.master.bind('<Left>', self.previous_image)
        self.master.bind('<Right>', self.next_image)
        self.master.bind('<ButtonPress-3>', self.next_image)
        self.master.bind('<ButtonPress-2>', self.previous_image)
        self.master.bind('<ButtonPress-1>', self.on_mouse_down)
        self.master.bind('<B1-Motion>', self.on_mouse_drag)
        self.master.bind('<ButtonRelease-1>', self.on_mouse_up)

        self.master.bind('<KeyPress-Shift_L>', self.enable_selection_mode)
        self.master.bind('<KeyPress-Control_L>', self.enable_selection_mode)
        self.master.bind('<KeyRelease-Shift_L>', self.disable_selection_mode)
        self.master.bind('<KeyRelease-Control_L>', self.disable_selection_mode)

        self.image_canvas.bind('<Configure>', self.on_resize)

    def set_title(self, title):
        self.master.title(title)