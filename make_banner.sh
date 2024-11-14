#!/bin/bash
INPUT_PATH="../cave_maps/input_3d"
OUTPUT_PATH="../cave_maps/output"

echo "BOUNDING BOX"
python3 ./find_bounding_box.py $INPUT_PATH/Agate-Hardee_3Dpas.zip $INPUT_PATH/PotSpring_3Dpas.zip $INPUT_PATH/MBSP_3Dpas.zip $INPUT_PATH/'M2 Blue Cave_3Dpas.zip' $INPUT_PATH/'M2 Blue Cave_3Dpas.zip'

echo "Making Withlacoochee banner"
mkdir -p $OUTPUT_PATH/banner
python3 ./spelunca.py --width 33.7 --height 81.34 -r -o $OUTPUT_PATH/banner/hardee_banner.svg --bounding_box $INPUT_PATH/'M2 Blue Cave_3Dpas.zip' $INPUT_PATH/Agate-Hardee_3Dpas.zip
python3 ./spelunca.py --width 33.7 --height 81.34 -r -o $OUTPUT_PATH/banner/madison_banner.svg --bounding_box $INPUT_PATH/'M2 Blue Cave_3Dpas.zip' $INPUT_PATH/MBSP_3Dpas.zip
python3 ./spelunca.py --width 33.7 --height 81.34 -r -o $OUTPUT_PATH/banner/M2_banner.svg $INPUT_PATH/'M2 Blue Cave_3Dpas.zip'
python3 ./spelunca.py --width 33.7 --height 81.34 -r -o $OUTPUT_PATH/banner/pot_banner.svg --bounding_box $INPUT_PATH/'M2 Blue Cave_3Dpas.zip' $INPUT_PATH/PotSpring_3Dpas.zip
python3 ./spelunca.py --width 33.7 --height 81.34 -r -o $OUTPUT_PATH/banner/little_coochee_banner.svg --bounding_box $INPUT_PATH/'M2 Blue Cave_3Dpas.zip' $INPUT_PATH/'little coochie_3Dpas.zip'
echo ""

