#!/bin/bash
INPUT_PATH="../cave_maps/input_3d"
OUTPUT_PATH="../cave_maps/output"

echo "BOUNDING BOX"
BOUNDING_BOX=$(python3 ./find_bounding_box.py $INPUT_PATH/Agate-Hardee_3Dpas.zip $INPUT_PATH/PotSpring_3Dpas.zip $INPUT_PATH/MBSP_3Dpas.zip $INPUT_PATH/'M2 Blue Cave_3Dpas.zip' $INPUT_PATH/'M2 Blue Cave_3Dpas.zip')

echo "Making Withlacoochee banner"
# TODO: fix depth scaling. It needs to be the same for every cave.
mkdir -p $OUTPUT_PATH/banner
python3 ./spelunca.py --width 33.7 --height 81.34 -r --set_bounding_box $BOUNDING_BOX -o $OUTPUT_PATH/banner/hardee_banner.svg         $INPUT_PATH/Agate-Hardee_3Dpas.zip
python3 ./spelunca.py --width 33.7 --height 81.34 -r --set_bounding_box $BOUNDING_BOX -o $OUTPUT_PATH/banner/madison_banner.svg        $INPUT_PATH/MBSP_3Dpas.zip
python3 ./spelunca.py --width 33.7 --height 81.34 -r --set_bounding_box $BOUNDING_BOX -o $OUTPUT_PATH/banner/M2_banner.svg             $INPUT_PATH/'M2 Blue Cave_3Dpas.zip'
python3 ./spelunca.py --width 33.7 --height 81.34 -r --set_bounding_box $BOUNDING_BOX -o $OUTPUT_PATH/banner/pot_banner.svg            $INPUT_PATH/PotSpring_3Dpas.zip
python3 ./spelunca.py --width 33.7 --height 81.34 -r --set_bounding_box $BOUNDING_BOX -o $OUTPUT_PATH/banner/little_coochee_banner.svg $INPUT_PATH/'little coochie_3Dpas.zip'
echo ""

