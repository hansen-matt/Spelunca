#!/bin/bash
INPUT_PATH="../cave_maps/input_3d"
OUTPUT_PATH="../cave_maps/output"

echo "Making Madison map"
mkdir -p $OUTPUT_PATH/madison
python3 ./spelunca.py -o $OUTPUT_PATH/madison/map.svg $INPUT_PATH/MBSP_3Dpas.zip
echo ""

echo "Making Madison mini map"
python3 ./spelunca.py -o $OUTPUT_PATH/madison/mini_map.svg --inset_x1 35 --inset_x2 65 --inset_y1 30 --inset_y2 60 $INPUT_PATH/MBSP_3Dpas.zip
echo ""

echo "Making Madison depth scale"
python3 ./spelunca.py -o $OUTPUT_PATH/madison/depth_scale.svg --depth_scale $INPUT_PATH/MBSP_3Dpas.zip
echo ""

echo "Making Pot Spring map"
mkdir -p $OUTPUT_PATH/pot
python3 ./spelunca.py -o $OUTPUT_PATH/pot/map.svg --bounding_box $INPUT_PATH/MBSP_3Dpas.zip $INPUT_PATH/PotSpring_3Dpas.zip
echo ""

echo "Making M2 map"
mkdir -p $OUTPUT_PATH/m2
python3 ./spelunca.py -o $OUTPUT_PATH/m2/map.svg $INPUT_PATH/'M2 Blue Cave_3Dpas.zip' --width=24 --height=36
echo ""

echo "Making Manatee map"
mkdir -p $OUTPUT_PATH/manatee
python3 ./spelunca.py -o $OUTPUT_PATH/manatee/map.svg $INPUT_PATH/Manatee_3Dpas.zip
echo ""

echo "Making Manatee depth scale"
python3 ./spelunca.py -o $OUTPUT_PATH/manatee/depth_scale.svg --depth_scale $INPUT_PATH/Manatee_3Dpas.zip
echo ""

echo "Making Withlacoochee banner"
mkdir -p $OUTPUT_PATH/banner
python3 ./spelunca.py --width 33.7 --height 81.34 -o $OUTPUT_PATH/banner/madison_banner.svg --bounding_box $INPUT_PATH/'M2 Blue Cave_3Dpas.zip' $INPUT_PATH/MBSP_3Dpas.zip
python3 ./spelunca.py --width 33.7 --height 81.34 -o $OUTPUT_PATH/banner/M2_banner.svg $INPUT_PATH/'M2 Blue Cave_3Dpas.zip'
python3 ./spelunca.py --width 33.7 --height 81.34 -o $OUTPUT_PATH/banner/pot_banner.svg --bounding_box $INPUT_PATH/'M2 Blue Cave_3Dpas.zip' $INPUT_PATH/PotSpring_3Dpas.zip
echo ""


