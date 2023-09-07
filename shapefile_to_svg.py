#!/usr/bin/python3

import shapefile
import svgwrite
from svgwrite import cm, mm

# Input shapefile path (update with your file path)
shapefile_path = 'input_3d/MBSP_3Dpas.shp'

# Output SVG file path (update with your desired output file path)
output_svg_path = 'madison.svg'

# Create an SVG drawing
svg_document = svgwrite.Drawing(output_svg_path, profile='tiny', size=(210*mm, 297*mm))

# Open the shapefile for reading
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
                    # Extract only X and Y coordinates
                    xy_points = [(x, y) for x, y, z in points if x is not None and y is not None]
                    if xy_points:
                        svg_document.add(svg_document.polygon(points=xy_points, fill='none', stroke='black', stroke_width=0.5*mm))

            # Handle other geometry types (e.g., Point, LineString)
            elif geometry.shapeType == shapefile.POINT:
                if len(geometry.points[0]) >= 2 and None not in geometry.points[0][:2]:
                    x, y = geometry.points[0][:2]  # Ignore the Z coordinate for points
                    svg_document.add(svg_document.circle(center=(x, y), r=2*mm, fill='red'))

            elif geometry.shapeType == shapefile.POLYLINE:
                points = geometry.points
                # Extract only X and Y coordinates
                xy_points = [(x, y) for x, y, z in points if x is not None and y is not None]
                if xy_points:
                    svg_document.add(svg_document.polyline(points=xy_points, fill='none', stroke='black', stroke_width=0.5*mm))

except shapefile.ShapefileException as e:
    print(f"Error processing shapefile: {str(e)}")

# Save the SVG file
svg_document.save()
print(f"SVG file saved to {output_svg_path}")

