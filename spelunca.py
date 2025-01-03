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
msg = "Generate SVG cave maps from 3d shapefiles exported by Compass"
parser = argparse.ArgumentParser(description = msg)
parser.add_argument("filename",  help = "Set input 3d passage shapefile (.zip)", default="")
parser.add_argument("-o", "--output", help = "Filename for the output image", default="output.svg")
parser.add_argument("--bounding_box", help = "Derive bounding box from a different shapefile. Useful for putting multiple caves on a single map")
parser.add_argument("--set_bounding_box", type=float, nargs=6, help="Set the bounding box and depth range with a list of 6 values (use find_bounding_box.py)")
parser.add_argument("--scale_factor", help="Set the scale factor, feet per cm", default=30, type=float)
parser.add_argument("--inset_x1", help = "Starting point for inset, expressed as a % of width (0-100)", default=0, type=float)
parser.add_argument("--inset_x2", help = "Ending point for inset, expressed as a % of width (0-100)", default=100, type=float)
parser.add_argument("--inset_y1", help = "Starting point for inset, expressed as a % of height (0-100)", default=0, type=float)
parser.add_argument("--inset_y2", help = "Ending point for inset, expressed as a % of height (0-100)", default=100, type=float)
parser.add_argument("--min_depth", help = "Shallowest depth to include. More negative is deeper", default=float('inf'), type=float)
parser.add_argument("--max_depth", help = "Deepest depth to include. More negative is deeper", default=-float('inf'), type=float)
parser.add_argument("-u", "--utm_zone", help = "UTM zone for map projection", default=17, type=int)
parser.add_argument("-b", "--border", help="Add a border around the image", action='store_true')
parser.add_argument("-r", "--rainbow", help="Use an exaggerated color scale for depth", action='store_true')
parser.add_argument("--border-offset", help="Offset from edge to border, in inches", default=0.5, type=float)
parser.add_argument("--width", help="Width of image in inches", default=36, type=float)
parser.add_argument("--height", help="Height of image in inches", default=24, type=float)
parser.add_argument("--depth_scale", help="Output a depth scale gradient", action='store_true')
args = parser.parse_args()

# Input shapefile path (update with your file path)
shapefile_path = args.filename
if shapefile_path == "":
    parser.print_help()
    exit()

if args.bounding_box:
    bbox_path = args.bounding_box
else:
    bbox_path = shapefile_path

# colors for depth
if args.rainbow:
    depth_color = plt.cm.gist_rainbow
else:
    depth_color = plt.cm.Blues_r

# Output SVG file path (update with your desired output file path)
output_svg_path = args.output

# Create an SVG drawing
svg_document = svgwrite.Drawing(output_svg_path, profile='full', size=(args.width*inch, args.height*inch))
inkscape = Inkscape(svg_document)

# Add a border
if args.border:
    border_layer = inkscape.layer(label="border", locked=True)
    svg_document.add(border_layer)
    border_offset = args.border_offset
    border = svg_document.rect((border_offset*inch,border_offset*inch), ((args.width-2*border_offset)*inch, (args.height-2*border_offset)*inch), fill='none', stroke='black', stroke_width=1*mm)
    border_layer.add(border)

# Add a layer for the map
map_layer = inkscape.layer(label="depth_map", locked=False)
svg_document.add(map_layer)

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
    rgb = np.round( np.multiply(rgb, 255))
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def get_color(depth, depth_color, depth_norm):
    fill_color = depth_color(depth_norm(depth))
    hex_color = rgb_to_hex(fill_color)
    return hex_color

def get_gradient(start_xy, start_depth, stop_xy, stop_depth, depth_color, depth_norm):
    start_color = get_color(start_depth, depth_color, depth_norm)
    stop_color  = get_color(stop_depth , depth_color, depth_norm)
    if start_depth == stop_depth: # don't need a gradient
        return start_color

    minx = min( start_xy[0], stop_xy[0] )
    miny = min( start_xy[1], stop_xy[1] )
    mins = (minx, miny)

    maxx = max( start_xy[0], stop_xy[0] )
    maxy = max( start_xy[1], stop_xy[1] )
    maxs = (maxx, maxy)

    dims = np.subtract(maxs, mins)
    if max(dims) <= 0.001: # avoid divide by zero warnings
        dims = (0.001, 0.001)

    start = np.divide(np.subtract(start_xy, mins), dims)
    stop  = np.divide(np.subtract(stop_xy, mins), dims)

    gradient = svgwrite.gradients.LinearGradient(start, stop)
    gradient.spreadMethod = 'pad'
    gradient.gradientUnits = 'objectBoundingBox'

    gradient.add_stop_color(0.0, start_color)
    gradient.add_stop_color(1.0, stop_color)

    return gradient

def in_range(value, minimum, maximum):
    if value < minimum:
        return False
    elif value > maximum:
        return False
    else:
        return True

def should_make_polygon(offset_xy, points_z):
    x = [x for x,y in offset_xy]
    y = [y for x,y in offset_xy]
    min_depth = np.min(points_z)
    max_depth = np.max(points_z)

    if np.max(x) > max_x:
        return False
    elif np.min(x) < min_x:
        return False
    elif np.max(y) > max_y:
        return False
    elif np.min(y) < min_y:
        return False
    
    if min_depth > args.min_depth:
        return False
    elif max_depth < args.max_depth:
        return False
    else:
        return True

def make_depth_scale(svg_document, min_depth, max_depth):
    depth_step = (max_depth - min_depth)/1000
    for x in range(0, 1000):
        offset_xy = [[x, 0], [x, 100], [x+2, 100], [x+2, 0], [x, 0]]
        depth = min_depth + x*depth_step
        color = get_color(depth, depth_color, depth_norm)
        polygon = svg_document.polygon(points=offset_xy, fill=color)
        map_layer.add(polygon)

def make_polygon(offset_xy, color, svg_document):
    polygon = svg_document.polygon(points=offset_xy, fill=color)
    return polygon

def make_polygon_list(shp):
    polygon_list = [];
    # Loop through shapefile records
    for shape_record in shp.iterShapeRecords():
        # Extract the geometry
        geometry = shape_record.shape

        # Handle 3D polygons (shapefile.POLYGONZ). Ignore the Z-coordinate for projection, but use it for color
        if geometry.shapeType == shapefile.POLYGONZ:
            for part in geometry.parts:
                points_xy  = geometry.points
                points_z   = geometry.z

                min_depth = np.min(points_z)

                projected_xy = [projector.transform(x, y) for x, y in points_xy]
                scaled_xy = np.multiply(projected_xy, scale_factor_xy)

                offset_xy = np.subtract(scaled_xy, offset)

                start_xy = np.divide(np.add(offset_xy[0], offset_xy[3]),2)
                end_xy   = np.divide(np.add(offset_xy[1], offset_xy[2]),2)
                start_depth = (points_z[0]+points_z[3])/2
                end_depth   = (points_z[1]+points_z[2])/2

                if scaled_xy_is_good(scaled_xy):
                    if should_make_polygon(offset_xy, points_z):

                        color = get_color(min_depth, depth_color, depth_norm)
                        gradient = get_gradient(start_xy, start_depth, end_xy, end_depth, depth_color, depth_norm)

                        polygon = make_polygon(offset_xy, color, svg_document)
                        polygon_list.append( (min_depth, polygon, gradient) )

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

shapefile_encoding = "ISO8859-1"

# Find the bounding box and offset
try:
    with shapefile.Reader(bbox_path, encoding=shapefile_encoding) as shp:
        if args.set_bounding_box:
            scaled_bbox = [[args.set_bounding_box[0], args.set_bounding_box[1]], [args.set_bounding_box[2], args.set_bounding_box[3]]]
            shallowest = args.set_bounding_box[4]
            deepest = args.set_bounding_box[5]
        else:
           bbox = [(shp.bbox[0], shp.bbox[2], shp.zbox[0]), (shp.bbox[1], shp.bbox[3], shp.zbox[1])]
           transformed_bbox = [projector.transform(x, y) for x, y, z in bbox]
           scaled_bbox = np.multiply(transformed_bbox, scale_factor_xy)

           # Depth limits for colors
           find_depth_limits(shp)

        # get the min x, and what would have been the max y, because y is inverted with the scale factor so max is min
        offset = [scaled_bbox[0][0] - 200, scaled_bbox[1][1] - 400]

        depth_norm = plt.Normalize(vmin=10*math.floor(deepest/10), vmax=0)

except shapefile.ShapefileException as e:
    print(f"Error processing shapefile: {str(e)}")

# Set limits for x,y

min_x = args.inset_x1 * args.width
min_y = args.inset_y1 * args.height
max_x = args.inset_x2 * args.width
max_y = args.inset_y2 * args.height

if args.depth_scale:
    make_depth_scale(svg_document, shallowest, deepest)
else:
    # Process the passages in the shapefile into polygons
    try:
        with shapefile.Reader(shapefile_path, encoding=shapefile_encoding) as shp:
            polygon_list = make_polygon_list(shp)

            for polygon_depth in polygon_list:
                polygon = polygon_depth[1]
                gradient = polygon_depth[2]
                if type(gradient) is svgwrite.gradients.LinearGradient:
                    gradient = map_layer.add(gradient)
                polygon.fill(gradient)
                map_layer.add(polygon)
    
    except shapefile.ShapefileException as e:
        print(f"Error processing shapefile: {str(e)}")

print(f"Depth range: {shallowest} to {deepest}")
# Save the SVG file
svg_document.save()
print(f"SVG file saved to {output_svg_path}")

