import argparse
import os


def parse_arguments():
    parser = argparse.ArgumentParser(description="inbac - interactive batch cropper")
    parser.add_argument("input_dir", nargs="?", help="input directory (defaults to current working directory)", default=os.getcwd())
    parser.add_argument("output_dir", nargs="?", help="output directory (defaults to folder crops in input directory)", default=argparse.SUPPRESS)
    parser.add_argument("-a", "--aspect_ratio", type=int, nargs=2, help="selection should have specified aspect ratio")
    parser.add_argument("-r", "--resize", type=int, nargs=2, help="cropped image will be resized to specified width and height")
    parser.add_argument("-s", "--selection_box_color", help="color of the selection box (default is black)", default="black")
    parser.add_argument("-w", "--window_size", type=int, nargs=2, help="initial window size (default is 800x600)", default=[800, 600])
    parser.add_argument("-p", "--preload_images", action="store_true", help="load all images to memory")

    args = parser.parse_args()
    args.output_dir = getattr(args, "output_dir", os.path.join(args.input_dir, "crops"))

    return args
