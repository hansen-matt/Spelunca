# Spelunca Cave Maps

This tool converts 3d shapefiles exported from Fountainware's Compass program into beautiful cave maps, colored by depth and in a SVG format for effortless rescaling.

## Python requirements

Using Ubuntu 24.04:

```
sudo apt install python3-fiona python3-pyshp python3-svgwrite python3-pyproj python3-matplotlib
```

## Using this code

This project works with any cave, with a little  work. The basic workflow is:
- Open the survey project in Compass and generate the plot
- From the plot, export a 3d shapefile, and make sure the "make zip" option is checked
- Add the zip file to the input_3d folder here
- Edit `make_maps.sh` to add the new project or see examples of how to run the script directly

The resulting SVG files can be edited in Inkscape or other programs.
