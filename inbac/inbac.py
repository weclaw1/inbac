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

    def run(self):
        self.view.master.mainloop()

def main():
    root = tk.Tk()
    app = Application(args.parse_arguments(), master=root)

    app.run()


if __name__ == "__main__":
    main()
