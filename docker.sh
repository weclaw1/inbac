#!/bin/bash

xhost +si:localuser:"$USER"
xhost +local:docker
docker run -it --rm -e DISPLAY="$DISPLAY" -v /tmp/.X11-unix:/tmp/.X11-unix -v "$HOME":/home $(docker build -q .)