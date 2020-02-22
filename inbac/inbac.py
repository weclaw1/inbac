import tkinter as tk
import os

from tkinter import filedialog, Tk
from argparse import Namespace

import inbac.parse_arguments as parse_args
from inbac.model import Model
from inbac.view import View
from inbac.controller import Controller


class Application():
    def __init__(self, args: Namespace, master: Tk):
        self.model: Model = Model(args)
        self.view: View = View(master, args.window_size)

        if args.input_dir is None:
            args.input_dir = filedialog.askdirectory(parent=master)
        args.output_dir = getattr(
            args, "output_dir", os.path.join(args.input_dir, "crops"))

        self.controller: Controller = Controller(self.model, self.view)

        if not os.path.exists(args.output_dir):
            self.controller.create_output_directory()

        self.view.controller = self.controller

    def run(self):
        self.view.master.mainloop()


def main():
    root = tk.Tk()
    root.title("inbac")
    app = Application(parse_args.parse_arguments(), master=root)

    app.run()


if __name__ == "__main__":
    main()
