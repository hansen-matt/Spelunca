#!/bin/bash

# set -x

echo "Making Madison map"
python3 main.py \
    --input_f input_3d/MBSP_3Dpas.zip \
    --output_f outputs/madison.svg \
    --overwrite_if_exists
echo ""

echo "Making Pot Spring map"
python3 main.py \
    --input_f  input_3d/PotSpring_3Dpas.zip \
    --output_f outputs/pot_spring.svg \
    --overwrite_if_exists \
    --bounding_box input_3d/MBSP_3Dpas.zip \
    --input_f  input_3d/PotSpring_3Dpas.zip
echo ""

echo "Making Cavern inset"
python3 main.py \
    --input_f input_3d/MBSP_3Dpas.zip \
    --output_f outputs/madison_inset.svg \
    --overwrite_if_exists \
    --inset_x1 47 \
    --inset_x2 65 \
    --inset_y1 23 \
    --inset_y2 40 \
    --max_depth -100
echo ""

echo "Making depth scale"
python3 main.py \
    --input_f input_3d/MBSP_3Dpas.zip \
    --output_f outputs/depth_scale.svg \
    --overwrite_if_exists \
    --use_depth_scale
echo ""
