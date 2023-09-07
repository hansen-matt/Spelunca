#!/usr/bin/python3

import shapefile
import svgwrite
from svgwrite import cm, mm
import pyproj

# Input shapefile path (update with your file path)
shapefile_path = 'input_3d/MBSP_3Dprism.shp'

# Output SVG file path (update with your desired output file path)
output_svg_path = 'madison.svg'

# Create an SVG drawing
svg_document = svgwrite.Drawing(output_svg_path, profile='tiny', size=(210*mm, 297*mm))

# Define the UTM projection suitable for your area of interest
utm_zone = 17  # Modify this according to your area
projector = pyproj.Transformer.from_crs("EPSG:4326", f"EPSG:326{utm_zone}", always_xy=True)

# Define the scale factor for 100 feet = 1 inch
scale_factor = 100.0 / 12.0  # Convert 100 feet to inches

# Open the shapefile for reading
polygonz_count = 0
no_data_count = 0
try:
    with shapefile.Reader(shapefile_path) as shp:

        # Loop through shapefile records
        for shape_record in shp.iterShapeRecords():

            # Extract the geometry
            geometry = shape_record.shape

            # Handle 3D polygons (shapefile.POLYGONZ) by ignoring the Z-coordinate
            if geometry.shapeType == shapefile.POLYGONZ:
                for part in geometry.parts:
                    points = geometry.points[part:part + geometry.parts[0]]
                    xy_points = [projector.transform(y, x) for x, y, z in points]
                    projected_points = [(x * scale_factor, y * scale_factor) for x, y in xy_points]

                    if projected_points:
                        svg_document.add(svg_document.polygon(points=projected_points, fill='none', stroke='black', stroke_width=0.5*mm))
                        polygonz_count += 1
                    else:
                        no_data_count += 1
                        print(f"no data {no_data_count}")
                        print(shape_record)
                        print(geometry)
                        print(geometry.parts)
                        print(points)

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

