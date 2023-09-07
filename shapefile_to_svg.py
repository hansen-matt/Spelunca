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
with shapefile.Reader(shapefile_path) as shp:

    # Loop through shapefile records
    for shape_record in shp.iterShapeRecords():

        # Extract the geometry
        geometry = shape_record.shape

        # Create SVG elements for different geometry types (e.g., Point, LineString, Polygon)
        if geometry.shapeType == shapefile.POINT:
            x, y = geometry.points[0]
            svg_document.add(svg_document.circle(center=(x, y), r=2*mm, fill='red'))

        elif geometry.shapeType == shapefile.POLYLINE:
            points = geometry.points
            svg_document.add(svg_document.polyline(points=points, fill='none', stroke='black', stroke_width=0.5*mm))

        elif geometry.shapeType == shapefile.POLYGON:
            points = geometry.points
            svg_document.add(svg_document.polygon(points=points, fill='none', stroke='black', stroke_width=0.5*mm))

# Save the SVG file
svg_document.save()
print(f"SVG file saved to {output_svg_path}")

