# inbac

## Description

inbac is an **in**teractive **ba**tch **c**ropper made for quick cropping of images.  
I made this program because cropping thousands of images with image viewers or image manipulation programs was too slow.

## Usage

```
usage: inbac [-h] [-a ASPECT_RATIO ASPECT_RATIO] [-r RESIZE RESIZE]
             [-s SELECTION_BOX_COLOR] [-w WINDOW_SIZE WINDOW_SIZE] [-p]
             [input_dir] [output_dir]

inbac - interactive batch cropper

Left Mouse Button                 - select part of image

Z                                 - save selection and go to the next picture

X                                 - save selection and stay on the same picture

Right Arrow or Right Mouse Button - go to next picture

Left Arrow or Left Mouse Button   - go to previous picture

positional arguments:
  input_dir             input directory (defaults to current working
                        directory)
  output_dir            output directory (defaults to folder crops in input
                        directory)

optional arguments:
  -h, --help            show this help message and exit
  -a ASPECT_RATIO ASPECT_RATIO, --aspect_ratio ASPECT_RATIO ASPECT_RATIO
                        selection should have specified aspect ratio
  -r RESIZE RESIZE, --resize RESIZE RESIZE
                        cropped image will be resized to specified width and
                        height
  -s SELECTION_BOX_COLOR, --selection_box_color SELECTION_BOX_COLOR
                        color of the selection box (default is black)
  -w WINDOW_SIZE WINDOW_SIZE, --window_size WINDOW_SIZE WINDOW_SIZE
                        initial window size (default is 800x600)
  -p, --preload_images  load all images to memory
 ```