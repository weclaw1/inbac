class Model():
    def __init__(self, args):
        self.args = args
        self.images = []
        self.selection_box = None
        self.press_coord = (0, 0)
        self.move_coord = (0, 0)
        self.canvas_image = None
        self.canvas_image_dimensions = (0, 0)
        self.current_image = None
        self.enabled_selection_mode = False
        self.box_selected = False
        self.current_file = 0