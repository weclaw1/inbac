import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="inbac - interactive batch cropper")
    parser.add_argument("-f", "--fixed_aspect_ratio", help="selection will have fixed aspect ratio", action="store_value")
    parser.add_argument("-arx",  "--aspect_ratio_x", type=int, help="aspect ratio x (default 1)", default=1)
    parser.add_argument("-ary",  "--aspect_ratio_y", type=int, help="aspect ratio y (default 1)", default=1)
    parser.add_argument("-r",  "--resize", type=int, help="aspect ratio y (default 1)", default=1)