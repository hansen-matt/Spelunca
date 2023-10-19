#!/bin/bash
echo "Making Madison map"
python3 ./shapefile_to_svg.py -o madison.svg -b input_3d/MBSP_3Dpas.zip
echo ""

echo "Making Pot Spring map"
python3 ./shapefile_to_svg.py -o pot_spring.svg --bounding_box input_3d/MBSP_3Dpas.zip input_3d/PotSpring_3Dpas.zip
echo ""

echo "Making Cavern inset"
python3 ./shapefile_to_svg.py -o madison_inset.svg --inset_x1 47 --inset_x2 65 --inset_y1 23 --inset_y2 40 --max_depth -100 input_3d/MBSP_3Dpas.zip
echo ""

echo "Making depth scale"
python3 ./shapefile_to_svg.py -o depth_scale.svg --depth_scale input_3d/MBSP_3Dpas.zip
echo ""
