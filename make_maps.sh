#!/bin/bash
echo "Making Madison map"
python3 ./shapefile_to_svg.py -o madison.svg -b input_3d/MBSP_3Dpas.zip
echo ""

echo "Making Pot Spring map"
python3 ./shapefile_to_svg.py -o pot_spring.svg --bounding_box input_3d/MBSP_3Dpas.zip input_3d/PotSpring_3Dpas.zip
echo ""

echo "Making Cavern inset"
python3 ./shapefile_to_svg.py -o madison_inset.svg --inset_x1 10 --inset_x2 70 --inset_y1 20 --inset_y2 50 input_3d/MBSP_3Dpas.zip
echo ""
