#!/usr/bin/python3

import shapefile
import svgwrite
from svgwrite import cm, mm
import pyproj
import array
import math

# Input shapefile path (update with your file path)
shapefile_path = 'input_3d/MBSP_3Dprism.zip'

# Output SVG file path (update with your desired output file path)
output_svg_path = 'madison.svg'

# Create an SVG drawing
svg_document = svgwrite.Drawing(output_svg_path, profile='tiny', size=(210*mm, 297*mm))

# Define the UTM projection suitable for your area of interest
utm_zone = 17  # Modify this according to your area
projector = pyproj.Transformer.from_crs("EPSG:4326", f"EPSG:326{utm_zone}", always_xy=True)

# Define the scale factor for 100 feet = 1 inch
scale_factor = 100.0 / 12.0  # Convert 100 feet to inches


def is_finite_list_of_tuples(list_of_tuples):
  for tuple in list_of_tuples:
    for element in tuple:
      if not math.isfinite(element):
        return False
  return True


# Open the shapefile for reading
polygonz_count = -1 
no_data_count = -1
try:
    with shapefile.Reader(shapefile_path) as shp:
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

                    #xy_points = [projector.transform(y, x) for x, y, z in points]
                    #xy_points = [projector.transform(y, x) for x, y in points]
                    projected_points = [(x * scale_factor, y * scale_factor) for x, y in points_xy]

                    if projected_points:
                        if is_finite_list_of_tuples(projected_points):
                            svg_document.add(svg_document.polygon(points=projected_points, fill='none', stroke='black', stroke_width=0.5*mm))
                            polygonz_count += 1
                        else:
                            print(f"points {points}")
                            print(f"xy_points {xy_points}")
                            print(f"not finite? {projected_points}")
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

