#!/bin/bash
echo "Making Madison map"
python3 ./shapefile_to_svg.py -o madison.svg input_3d/MBSP_3Dpas.zip
echo ""

echo "Making Pot Spring map"
python3 ./shapefile_to_svg.py -o pot_spring.svg --bounding_box input_3d/MBSP_3Dpas.zip input_3d/PotSpring_3Dpas.zip
echo ""

echo "Making Cavern inset"
python3 ./shapefile_to_svg.py -o madison_inset.svg --inset_x1 47 --inset_x2 65 --inset_y1 23 --inset_y2 40 --max_depth -100 input_3d/MBSP_3Dpas.zip
echo ""

echo "Making Madison depth scale"
python3 ./shapefile_to_svg.py -o depth_scale.svg --depth_scale input_3d/MBSP_3Dpas.zip
echo ""

echo "Making M2 map"
python3 ./shapefile_to_svg.py -o M2.svg 'input_3d/M2 Blue Cave_3Dpas.zip'
echo ""

echo "Making Manatee map"
python3 ./shapefile_to_svg.py -o Manatee.svg 'input_3d/Manatee_3Dpas.zip'
echo ""

echo "Making Manatee depth scale"
python3 ./shapefile_to_svg.py -o Manatee_depth_scale.svg --depth_scale input_3d/Manatee_3Dpas.zip
echo ""
