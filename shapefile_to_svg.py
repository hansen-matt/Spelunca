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

# Argument parsing
msg = "Generate SVG cave maps from 3d shapefiles exported by Compass"
parser = argparse.ArgumentParser(description = msg)
parser.add_argument("filename", help = "Set input 3d passage shapefile (.zip)")
parser.add_argument("-i", "--inset", help = "Create an svg of a small region to use as an inset image")
parser.add_argument("--min_depth", help = "Shallowest depth to include. More negative is deeper", default=float('inf'), type=float)
parser.add_argument("--max_depth", help = "Deepest depth to include. More negative is deeper", default=-float('inf'), type=float)
args = parser.parse_args()

# Input shapefile path (update with your file path)
shapefile_path = 'input_3d/MBSP_3Dpas.zip'
shapefile_path_pot = 'input_3d/PotSpring_3Dpas.zip'
shapefile_prj_path = shapefile_path.replace("zip","prj");
shapefile_prj_path_pot = shapefile_path_pot.replace("zip","prj");

# Output SVG file path (update with your desired output file path)
output_svg_path = 'madison.svg'
output_svg_path_pot = 'pot_spring.svg'

# Create an SVG drawing
svg_document = svgwrite.Drawing(output_svg_path, profile='tiny', size=(36*inch, 24*inch))
svg_document_pot = svgwrite.Drawing(output_svg_path_pot, profile='tiny', size=(36*inch, 24*inch))
inkscape = Inkscape(svg_document)
inkscape_pot = Inkscape(svg_document_pot)

# Add a border
border_layer = inkscape.layer(label="border", locked=True)
svg_document.add(border_layer)
border = svg_document.rect((0.5*inch,0.5*inch), (35*inch, 23*inch), fill='none', stroke='black', stroke_width=1*mm)
border_layer.add(border)

# Add a layer for the map
map_layer = inkscape.layer(label="depth_map", locked=True)
svg_document.add(map_layer)

map_layer_pot = inkscape.layer(label="depth_map", locked=True)
svg_document_pot.add(map_layer_pot)

# Define the UTM projection suitable for your area of interest
utm_zone = 17  # Modify this according to your area
with open(shapefile_prj_path ,'r') as f:
        inProj = pyproj.Proj(f.read())
outProj = pyproj.Proj(f"EPSG:326{utm_zone}")
projector = pyproj.Transformer.from_proj(inProj, outProj)

# Define the scale factor for 30 feet = 1 inch
scale_factor = 12.0*2.54 / (30.0)  # Convert 30 feet to cm
# y is north up, PNG is positive down, so invert
scale_factor_xy = [scale_factor, -1*scale_factor]
scale_factor_xyz = [scale_factor, -1*scale_factor, scale_factor]

polygonz_count = -1 
no_data_count = -1
shallowest = -10000;
deepest = 0;
polygon_list = [];

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
    avg_depth = np.mean(points_z)
    max_depth = np.max(points_z)

    global shallowest
    global deepest
    shallowest = max(shallowest, min_depth)
    deepest = min(deepest, max_depth)

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

# Open the shapefile for reading
try:
    with shapefile.Reader(shapefile_path) as shp:
        print(shp)

        bbox = [(shp.bbox[0], shp.bbox[2], shp.zbox[0]), (shp.bbox[1], shp.bbox[3], shp.zbox[1])]
        transformed_bbox = [projector.transform(x, y) for x, y, z in bbox]
        scaled_bbox = np.multiply(transformed_bbox, scale_factor_xy)
        # get the min x, and what would have been the max y, because y is inverted with the scale factor so max is min
        offset = [scaled_bbox[0][0] - 200, scaled_bbox[1][1] - 400]

        # colors for depth
        depth_color = plt.cm.Blues_r
        #depth_norm = plt.Normalize(vmin=shp.zbox[0], vmax=shp.zbox[1])
        #depth_norm = plt.Normalize(vmin=shp.zbox[0], vmax=0)
        depth_norm = plt.Normalize(vmin=-130, vmax=0)

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
                            polygonz_count += 1


        polygon_list.sort(key=lambda a: a[0])
        for polygon_depth in polygon_list:
            polygon = polygon_depth[1]
            map_layer.add(polygon)

except shapefile.ShapefileException as e:
    print(f"Error processing shapefile: {str(e)}")

polygon_list.clear()

# Open the shapefile for reading
try:
    with shapefile.Reader(shapefile_path_pot) as shp:
        print(shp)

        # Loop through shapefile records
        for shape_record in shp.iterShapeRecords():

            # Extract the geometry
            geometry = shape_record.shape

            # Handle 3D polygons (shapefile.POLYGONZ) by ignoring the Z-coordinate
            if geometry.shapeType == shapefile.POLYGONZ:
                for part in geometry.parts:
                    points_xy  = geometry.points #[part:part + geometry.parts[0]]
                    points_z   = geometry.z
                    points_xyz = [(x,y,z) for (x,y),z in zip(points_xy, points_z)]

                    projected_xy = [projector.transform(x, y) for x, y, z in points_xyz]
                    #scaled_xy = [(x * scale_factor, y * scale_factor) for x, y in projected_xy]
                    scaled_xy = np.multiply(projected_xy, scale_factor_xy)

                    offset_xy = np.subtract(scaled_xy, offset)

                    if scaled_xy.all():
                        if is_finite_list_of_tuples(scaled_xy):
                            min_depth = np.min(points_z)
                            if min_depth > args.min_depth:
                                continue
                            avg_depth = np.mean(points_z)
                            max_depth = np.max(points_z)
                            if max_depth < args.max_depth:
                                continue
                            fill_color = depth_color(depth_norm(min_depth))
                            hex_color = rgb_to_hex(fill_color)
                            shallowest = max(shallowest, min_depth)
                            deepest = min(deepest, max_depth)

                            polygon = svg_document_pot.polygon(points=offset_xy, fill=hex_color) #, stroke='none', stroke_width=0.0*mm)
                            polygon_list.append( (min_depth, polygon) )
                            polygonz_count += 1


        polygon_list.sort(key=lambda a: a[0])
        for polygon_depth in polygon_list:
            polygon = polygon_depth[1]
            map_layer_pot.add(polygon)

except shapefile.ShapefileException as e:
    print(f"Error processing shapefile: {str(e)}")

print(f"Minimum depth: {shallowest}")
print(f"Maximum depth: {deepest}")
print(f"polygonz count {polygonz_count}")
# Save the SVG file
svg_document.save()
svg_document_pot.save()
print(f"SVG file saved to {output_svg_path}")

