import fiona
import svgwrite

# Open the shapefile
with fiona.open("my_shapefile.shp") as shapefile:
  # Create an SVG writer
  writer = svgwrite.Drawing()

  # Iterate over the features in the shapefile
  for feature in shapefile:
    # Get the geometry of the feature
    geometry = feature["geometry"]

    # Create a new SVG element for the feature
    element = writer.shape(geometry)

    # Add the element to the SVG writer
    writer.add(element)

  # Write the SVG to a file
  writer.write("my_shapefile.svg")
