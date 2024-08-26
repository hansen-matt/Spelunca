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
parser.add_argument("-o", "--output", help = "Filename for the output image", default="output.svg")
parser.add_argument("--bounding_box", help = "Derive bounding box from a different shapefile. Useful for putting multiple caves on a single map")
parser.add_argument("--inset_x1", help = "Starting point for inset, expressed as a % of width (0-100)", default=0, type=float)
parser.add_argument("--inset_x2", help = "Ending point for inset, expressed as a % of width (0-100)", default=100, type=float)
parser.add_argument("--inset_y1", help = "Starting point for inset, expressed as a % of height (0-100)", default=0, type=float)
parser.add_argument("--inset_y2", help = "Ending point for inset, expressed as a % of height (0-100)", default=100, type=float)
parser.add_argument("--min_depth", help = "Shallowest depth to include. More negative is deeper", default=float('inf'), type=float)
parser.add_argument("--max_depth", help = "Deepest depth to include. More negative is deeper", default=-float('inf'), type=float)
parser.add_argument("-u", "--utm_zone", help = "UTM zone for map projection", default=17, type=int)
parser.add_argument("-b", "--border", help="Add a border around the image", action='store_true')
parser.add_argument("--border-offset", help="Offset from edge to border, in inches", default=0.5, type=float)
parser.add_argument("--width", help="Width of image in inches", default=36, type=float)
parser.add_argument("--height", help="Height of image in inches", default=24, type=float)
parser.add_argument("--depth_scale", help="Output a depth scale gradient", action='store_true')
args = parser.parse_args()

# Input shapefile path (update with your file path)
shapefile_path = args.filename

if args.bounding_box:
    bbox_path = args.bounding_box
else:
    bbox_path = shapefile_path

# Output SVG file path (update with your desired output file path)
output_svg_path = args.output

# Create an SVG drawing
svg_document = svgwrite.Drawing(output_svg_path, profile='tiny', size=(args.width*inch, args.height*inch))
inkscape = Inkscape(svg_document)

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
    rgb = np.round( np.multiply(rgb, 255))
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def get_color(depth, depth_color, depth_norm):
    fill_color = depth_color(depth_norm(depth))
    hex_color = rgb_to_hex(fill_color)
    return hex_color

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
    print(depth_step)
    for x in range(0, 1000):
        offset_xy = [[x, 0], [x, 100], [x+2, 100], [x+2, 0], [x, 0]]
        depth = min_depth + x*depth_step
        color = get_color(depth, depth_color, depth_norm)
        polygon = svg_document.polygon(points=offset_xy, fill=color) #, stroke='none', stroke_width=0.0*mm)
        map_layer.add(polygon)

def make_polygon(offset_xy, color, svg_document):
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
                    if should_make_polygon(offset_xy, points_z):
                        color = get_color(min_depth, depth_color, depth_norm)

                        polygon = make_polygon(offset_xy, color, svg_document)
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

# Set limits for x,y

min_x = args.inset_x1 * args.width
min_y = args.inset_y1 * args.height
max_x = args.inset_x2 * args.width
max_y = args.inset_y2 * args.height

print(f"minx {min_x} min_y {min_y} maxx {max_x} maxy {max_y}")

if args.depth_scale:
    make_depth_scale(svg_document, shallowest, deepest)
else:
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

print(f"Minimum depth: {shallowest}")
print(f"Maximum depth: {deepest}")
# Save the SVG file
svg_document.save()
print(f"SVG file saved to {output_svg_path}")

