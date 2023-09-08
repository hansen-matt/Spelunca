#!/usr/bin/python3

import shapefile
import svgwrite
from svgwrite import cm, mm
import pyproj
import array
import math
import numpy as np
import matplotlib.pyplot as plt

# Input shapefile path (update with your file path)
shapefile_path = 'input_3d/MBSP_3Dprism.zip'
shapefile_prj_path = shapefile_path.replace("zip","prj");

# Output SVG file path (update with your desired output file path)
output_svg_path = 'madison.svg'

# Create an SVG drawing
svg_document = svgwrite.Drawing(output_svg_path, profile='full') #, size=(17*in, 10*in))

# Define the UTM projection suitable for your area of interest
utm_zone = 17  # Modify this according to your area
with open(shapefile_prj_path ,'r') as f:
        inProj = pyproj.Proj(f.read())
outProj = pyproj.Proj(f"EPSG:326{utm_zone}")
projector = pyproj.Transformer.from_proj(inProj, outProj)

# Define the scale factor for 10 feet = 1 inch
scale_factor = 12.0*2.54 / (10.0)  # Convert 100 feet to cm
# y is north up, PNG is positive down, so invert
scale_factor_xy = [scale_factor, -1*scale_factor]
scale_factor_xyz = [scale_factor, -1*scale_factor, scale_factor]

def is_finite_list_of_tuples(list_of_tuples):
  for tuple in list_of_tuples:
    for element in tuple:
      if not math.isfinite(element):
        return False
  return True

def rgb_to_hex(rgb):
    rgb = np.round( np.multiply(rgb, 256))
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

# Open the shapefile for reading
polygonz_count = -1 
no_data_count = -1
try:
    with shapefile.Reader(shapefile_path) as shp:
        print(shp)

        bbox = [(shp.bbox[0], shp.bbox[2], shp.zbox[0]), (shp.bbox[1], shp.bbox[3], shp.zbox[1])]
        transformed_bbox = [projector.transform(x, y) for x, y, z in bbox]
        scaled_bbox = np.multiply(transformed_bbox, scale_factor_xy)
        # get the min x, and what would have been the max y, because y is inverted with the scale factor so max is min
        offset = [scaled_bbox[0][0], scaled_bbox[1][1]]

        # colors for depth
        depth_color = plt.cm.Blues_r
        #depth_norm = plt.Normalize(vmin=shp.zbox[0], vmax=shp.zbox[1])
        depth_norm = plt.Normalize(vmin=shp.zbox[0], vmax=0)
        print(f"min depth={shp.zbox[0]}   max depth={shp.zbox[1]}")


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
                            avg_depth = np.mean(points_z)
                            fill_color = depth_color(depth_norm(avg_depth))
                            hex_color = rgb_to_hex(fill_color)
                            
                            svg_document.add(svg_document.polygon(points=offset_xy*cm, fill=hex_color, stroke='black', stroke_width=0.1*mm))
                            polygonz_count += 1
                        else:
                            print(f"points_xyz {points_xyz}")
                            print(f"projected_xy {projected_xy}")
                            print(f"scaled_xy {scaled_xy}")
                    else:
                        no_data_count += 1
                        print(f"no data {no_data_count}")
                        print(f"shape_record {shape_record}")
                        print(f"geometry {geometry}")
                        print(f"geometry.parts {geometry.parts}")
                        print(f"geometry.parts[0] {geometry.parts[0]}")
                        print(f"geometry.points {geometry.points}")
                        print(f"geometry.points[0] {geometry.points[0]}")
                        print(f"len(geometry.points) {len(geometry.points)}")
                        print(f"part {part}")
                        print(f"geometry.bbox {bbox}")
                        print(f"geometry.points {geometry.points[part:part + geometry.parts[0]]}")
                        print(f"points {points}")
                        print(f"shapeType {geometry.shapeTypeName}")
                        print("")

            # Handle other geometry types (e.g., Point, LineString)
            elif geometry.shapeType == shapefile.POINT:
                if len(geometry.points[0]) >= 2 and None not in geometry.points[0][:2]:
                    x, y = geometry.points[0][:2]  # Ignore the Z coordinate for points
                    projected_x, projected_y = (x * scale_factor, y*scale_factor)
                    svg_document.add(svg_document.circle(center=(projected_x, projected_y), r=2*mm, fill='red'))

            elif geometry.shapeType == shapefile.POLYLINE:
                points = geometry.points
                # Extract only X and Y coordinates
                xy_points = [(x * scale_factor , y * scale_factor ) for x, y, z in projector.transform(*zip(*points)) if x is not None and y is not None]
                if xy_points:
                    svg_document.add(svg_document.polyline(points=xy_points, fill='none', stroke='black', stroke_width=0.5*mm))

except shapefile.ShapefileException as e:
    print(f"Error processing shapefile: {str(e)}")

print(f"polygonz count {polygonz_count}")
# Save the SVG file
svg_document.save()
print(f"SVG file saved to {output_svg_path}")

