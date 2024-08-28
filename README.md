# Madison Project

Tools and data for the Madison map.

## Python requirements

Using Ubuntu 24.04:

```
sudo apt install python3-fiona python3-pyshp python3-svgwrite python3-pyproj python3-matplotlib
```

## Using this code

This project is not limited to making maps of Madison - it works with any cave, with some work. The basic workflow is:
- Open the survey project in Compass and generate the plot
- From the plot, export a 3d shapefile, and make sure the "make zip" option is checked
- Add the zip file to the input_3d folder here
- Edit `make_maps.sh` to add the new project or see examples of how to run the script directly
