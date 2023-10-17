#!/bin/bash
python3 ./shapefile_to_svg.py -o madison.svg -b input_3d/MBSP_3Dpas.zip
python3 ./shapefile_to_svg.py -o pot.svg --bounding-box input_3d/MBSP_3Dpas.zip input_3d/PotSpring_3Dpas.zip
