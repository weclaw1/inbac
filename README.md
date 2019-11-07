# inbac

![](https://raw.githubusercontent.com/weclaw1/inbac/master/resources/demo.gif)

## Description

inbac is an **in**teractive **ba**tch **c**ropper made for quick cropping of images.  
I made this program because cropping thousands of images with image viewers or image manipulation programs was too slow.

## Requirements
- [poetry](https://github.com/sdispater/poetry)
- tkinter

After installing above dependencies run `poetry install` in project directory to install remaining dependencies.

## Examples

`poetry run inbac /home/user/pictures/`  
Opens images in /home/user/pictures/ and saves cropped images to /home/user/pictures/crops

`poetry run inbac -a 1 1 -r 256 256 /home/user/pictures/ /home/user/crops/`  
Opens images in /home/user/pictures/ in 1:1 ratio selection mode and saves images resized to 256x256px in /home/user/crops/ 

## Usage

```
usage: inbac [-h] [-a ASPECT_RATIO ASPECT_RATIO] [-r RESIZE RESIZE]
             [-s SELECTION_BOX_COLOR] [-w WINDOW_SIZE WINDOW_SIZE]
             [-f IMAGE_FORMAT] [-q IMAGE_QUALITY]
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
  -f IMAGE_FORMAT, --image_format IMAGE_FORMAT
                        define the croped image format
  -q IMAGE_QUALITY, --image_quality IMAGE_QUALITY
                        define the croped image quality
 ```
