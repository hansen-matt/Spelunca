#!/bin/bash
echo "Making Madison map"
python3 ./shapefile_to_svg.py -o madison.svg -b input_3d/MBSP_3Dpas.zip
echo ""

echo "Making Pot Spring map"
python3 ./shapefile_to_svg.py -o pot_spring.svg --bounding_box input_3d/MBSP_3Dpas.zip input_3d/PotSpring_3Dpas.zip
