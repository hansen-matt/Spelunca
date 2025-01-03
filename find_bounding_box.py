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
parser.add_argument("filename", nargs="+",  help = "List input 3d passage shapefile (.zip), space separated", default="")
parser.add_argument("-u", "--utm_zone", help = "UTM zone for map projection", default=17, type=int)
parser.add_argument("--scale_factor", help="Set the scale factor, feet per cm", default=30, type=float)
args = parser.parse_args()

master_bbox = [[math.nan, math.nan], [math.nan, math.nan]]

shallowest = -float('inf');
deepest = float('inf');

def find_depth_limits(shp):
    global shallowest
    global deepest
    for shape_record in shp.iterShapeRecords():
        geometry = shape_record.shape
        if geometry.shapeType == shapefile.POLYGONZ:
            for part in geometry.parts:
                points_z = geometry.z
                min_depth = np.min(points_z)
                max_depth = np.max(points_z)
                shallowest= max(shallowest, min_depth)
                deepest = min(deepest, max_depth)

for shapefile_path in args.filename:
    # Input shapefile path
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
    scale_factor = 12.0*2.54 / (args.scale_factor)  # Convert 30 feet to cm
    # y is north up, PNG is positive down, so invert
    scale_factor_xy = [scale_factor, -1*scale_factor]
    
    shapefile_encoding = "ISO8859-1"
    
    # Find the bounding box 
    try:
        with shapefile.Reader(shapefile_path, encoding=shapefile_encoding) as shp:
            bbox = [(shp.bbox[0], shp.bbox[2], shp.zbox[0]), (shp.bbox[1], shp.bbox[3], shp.zbox[1])]
            transformed_bbox = [projector.transform(x, y) for x, y, z in bbox]
            scaled_bbox = np.multiply(transformed_bbox, scale_factor_xy)
            find_depth_limits(shp)

            master_bbox[0][0] = min(scaled_bbox[0][0], master_bbox[0][0])
            master_bbox[0][1] = max(scaled_bbox[0][1], master_bbox[0][1])
            master_bbox[1][0] = max(scaled_bbox[1][0], master_bbox[1][0])
            master_bbox[1][1] = min(scaled_bbox[1][1], master_bbox[1][1])
    
    except shapefile.ShapefileException as e:
        print(f"Error processing shapefile: {str(e)}")

print(master_bbox[0][0], " ", master_bbox[0][1], " ",master_bbox[1][0], " ",master_bbox[1][1]," ",shallowest," ",deepest)
