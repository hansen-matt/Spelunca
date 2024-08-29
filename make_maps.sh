#!/bin/bash
INPUT_PATH="../cave_maps/input_3d"
OUTPUT_PATH="../cave_maps/output"

echo "Making Madison map"
mkdir -p $OUTPUT_PATH/madison
python3 ./spelunca.py -o $OUTPUT_PATH/madison/map.svg $INPUT_PATH/MBSP_3Dpas.zip
echo ""

echo "Making Madison cavern inset"
python3 ./spelunca.py -o $OUTPUT_PATH/madison/cavern_inset.svg --inset_x1 47 --inset_x2 65 --inset_y1 23 --inset_y2 40 --max_depth -100 $INPUT_PATH/MBSP_3Dpas.zip
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
