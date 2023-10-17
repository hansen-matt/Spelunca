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

# Argument parsing
msg = "Generate SVG cave maps from 3d shapefiles exported by Compass"
parser = argparse.ArgumentParser(description = msg)
parser.add_argument("filename", nargs='?', help = "Set input 3d passage shapefile (.zip)", default="input_3d/MBSP_3Dpas.zip")
parser.add_argument("--bounding_box", help = "Derive bounding box from a different shapefile. Useful for putting multiple caves on a single map")
parser.add_argument("-i", "--inset", help = "Create an svg of a small region to use as an inset image")
parser.add_argument("--min_depth", help = "Shallowest depth to include. More negative is deeper", default=float('inf'), type=float)
parser.add_argument("--max_depth", help = "Deepest depth to include. More negative is deeper", default=-float('inf'), type=float)
parser.add_argument("-u", "--utm_zone", help = "UTM zone for map projection", default=17, type=int)
parser.add_argument("-b", "--border", help="Add a border around the image", action='store_true')
parser.add_argument("--border-offset", help="Offset from edge to border, in inches", default=0.5, type=float)
parser.add_argument("--width", help="Width of image in inches", default=36, type=float)
parser.add_argument("--height", help="Height of image in inches", default=24, type=float)
args = parser.parse_args()

# Input shapefile path (update with your file path)
shapefile_path = args.filename
shapefile_path_pot = 'input_3d/PotSpring_3Dpas.zip'

if args.bounding_box:
    bbox_path = args.bounding_box
else:
    bbox_path = shapefile_path

# Output SVG file path (update with your desired output file path)
output_svg_path = 'madison.svg'
output_svg_path_pot = 'pot_spring.svg'

# Create an SVG drawing
svg_document = svgwrite.Drawing(output_svg_path, profile='tiny', size=(args.width*inch, args.height*inch))
svg_document_pot = svgwrite.Drawing(output_svg_path_pot, profile='tiny', size=(args.width*inch, args.height*inch))
inkscape = Inkscape(svg_document)
inkscape_pot = Inkscape(svg_document_pot)

# Add a border
if args.border:
    border_layer = inkscape.layer(label="border", locked=True)
    svg_document.add(border_layer)
    border_offset = args.border_offset
    border = svg_document.rect((border_offset*inch,border_offset*inch), ((args.width-2*border_offset)*inch, (args.height-2*border_offset)*inch), fill='none', stroke='black', stroke_width=1*mm)
    border_layer.add(border)

# Add a layer for the map
map_layer = inkscape.layer(label="depth_map", locked=True)
svg_document.add(map_layer)

map_layer_pot = inkscape.layer(label="depth_map", locked=True)
svg_document_pot.add(map_layer_pot)

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

# Functions to check if all the elements in a tuple are valid
def is_finite_list_of_tuples(list_of_tuples):
  for tuple in list_of_tuples:
    for element in tuple:
      if not math.isfinite(element):
        return False
  return True

def scaled_xy_is_good(scaled_xy):
    return scaled_xy.all() and is_finite_list_of_tuples(scaled_xy)

# Colormap related functions
def rgb_to_hex(rgb):
    rgb = np.round( np.multiply(rgb, 256))
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def get_color(depth, depth_color, depth_norm):
    fill_color = depth_color(depth_norm(depth))
    hex_color = rgb_to_hex(fill_color)
    return hex_color

    
def should_make_polygon(points_z):
    min_depth = np.min(points_z)
    max_depth = np.max(points_z)

    if min_depth > args.min_depth:
        return False
    elif max_depth < args.max_depth:
        return False
    else:
        return True

def make_polygon(scaled_xy, offset, color, svg_document):
    offset_xy = np.subtract(scaled_xy, offset)
    polygon = svg_document.polygon(points=offset_xy, fill=color) #, stroke='none', stroke_width=0.0*mm)
    return polygon

def make_polygon_list(shp, svg_document):
    polygon_list = [];
    # Loop through shapefile records
    for shape_record in shp.iterShapeRecords():
        # Extract the geometry
        geometry = shape_record.shape

        # Handle 3D polygons (shapefile.POLYGONZ). Ignore the Z-coordinate for projection, but use it for color
        if geometry.shapeType == shapefile.POLYGONZ:
            for part in geometry.parts:
                points_xy  = geometry.points #[part:part + geometry.parts[0]]
                points_z   = geometry.z

                min_depth = np.min(points_z)

                projected_xy = [projector.transform(x, y) for x, y in points_xy]
                scaled_xy = np.multiply(projected_xy, scale_factor_xy)

                offset_xy = np.subtract(scaled_xy, offset)

                if scaled_xy_is_good(scaled_xy):
                    if should_make_polygon(points_z):
                        color = get_color(min_depth, depth_color, depth_norm)

                        polygon = make_polygon(scaled_xy, offset, color, svg_document)
                        polygon_list.append( (min_depth, polygon) )

    polygon_list.sort(key=lambda a: a[0])
    return polygon_list

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

# Find the bounding box and offset
try:
    with shapefile.Reader(bbox_path) as shp:
        bbox = [(shp.bbox[0], shp.bbox[2], shp.zbox[0]), (shp.bbox[1], shp.bbox[3], shp.zbox[1])]
        transformed_bbox = [projector.transform(x, y) for x, y, z in bbox]
        scaled_bbox = np.multiply(transformed_bbox, scale_factor_xy)
        # get the min x, and what would have been the max y, because y is inverted with the scale factor so max is min
        offset = [scaled_bbox[0][0] - 200, scaled_bbox[1][1] - 400]

        # colors for depth
        find_depth_limits(shp)
        depth_color = plt.cm.Blues_r
        depth_norm = plt.Normalize(vmin=10*math.floor(deepest/10), vmax=0)

except shapefile.ShapefileException as e:
    print(f"Error processing shapefile: {str(e)}")

# Process the passages in the shapefile into polygons
try:
    with shapefile.Reader(shapefile_path) as shp:
        print(shp)

        polygon_list = make_polygon_list(shp, svg_document)
        for polygon_depth in polygon_list:
            polygon = polygon_depth[1]
            map_layer.add(polygon)

except shapefile.ShapefileException as e:
    print(f"Error processing shapefile: {str(e)}")

# Open the shapefile for reading
try:
    with shapefile.Reader(shapefile_path_pot) as shp:
        print(shp)

        polygon_list = make_polygon_list(shp, svg_document_pot)
        for polygon_depth in polygon_list:
            polygon = polygon_depth[1]
            map_layer_pot.add(polygon)

except shapefile.ShapefileException as e:
    print(f"Error processing shapefile: {str(e)}")

print(f"Minimum depth: {shallowest}")
print(f"Maximum depth: {deepest}")
# Save the SVG file
svg_document.save()
svg_document_pot.save()
print(f"SVG file saved to {output_svg_path}")

