#!/usr/bin/python3

import shapefile
import svgwrite
from svgwrite import cm, mm, inch
from svgwrite.extensions import Inkscape
import pyproj
import array
import math
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
import tempfile
import zipfile
import sys

# Argument parsing
msg = "Determine a master bounding box from multiple 3d shapefiles"
parser = argparse.ArgumentParser(description = msg)
parser.add_argument("filename",  help = "Set input 3d passage shapefile (.zip)", default="")
args = parser.parse_args()

# Input shapefile path (update with your file path)
shapefile_path = args.filename
if shapefile_path == "":
    parser.print_help()
    exit()

## Figure out the projection
# First, unzip the zip file to a temp directory
temp_dir = tempfile.mkdtemp()
with zipfile.ZipFile(shapefile_path, "r") as zip_file:
    zip_file.extractall(temp_dir)
basename = os.path.basename(shapefile_path)
prj_path = temp_dir + "/" + basename.replace("zip","prj");

# Define the UTM projection suitable for your area of interest
with open(prj_path ,'r') as f:
        inProj = pyproj.Proj(f.read())
outProj = pyproj.Proj(f"EPSG:326{args.utm_zone}")
projector = pyproj.Transformer.from_proj(inProj, outProj)

# Define the scale factor for 30 feet = 1 inch
scale_factor = 12.0*2.54 / (30.0)  # Convert 30 feet to cm
# y is north up, PNG is positive down, so invert
scale_factor_xy = [scale_factor, -1*scale_factor]

shallowest = -float('inf');
deepest = float('inf');

shapefile_encoding = "ISO8859-1"

# Find the bounding box and offset
try:
    with shapefile.Reader(shapefile_path, encoding=shapefile_encoding) as shp:
        bbox = [(shp.bbox[0], shp.bbox[2], shp.zbox[0]), (shp.bbox[1], shp.bbox[3], shp.zbox[1])]
        transformed_bbox = [projector.transform(x, y) for x, y, z in bbox]
        scaled_bbox = np.multiply(transformed_bbox, scale_factor_xy)
        # get the min x, and what would have been the max y, because y is inverted with the scale factor so max is min
        offset = [scaled_bbox[0][0] - 200, scaled_bbox[1][1] - 400]

        print("Bounding box: ", scaled_bbox)
        sys.exit()


except shapefile.ShapefileException as e:
    print(f"Error processing shapefile: {str(e)}")



