#!/usr/bin/python3

import src.logger as logger
from src.arg_utils import CustomArgParser
from src.runner import Runner

if __name__ == "__main__":
    # Argument parsing
    parser = CustomArgParser(
        description="Generate SVG cave maps from 3D shapefiles exported by "
        "Compass"
    )

    parser.add_argument(
        "-i",
        "--input_f",
        nargs="?",
        help="Set input 3d passage shapefile (.zip)",
        required=True
        # default="input_3d/MBSP_3Dpas.zip",
    )

    parser.add_argument(
        "-o",
        "--output_f",
        help="Filename for the output image",
        required=True
        # default="output.svg",
    )

    parser.add_bool_argument(
        name="--overwrite_if_exists",
        help="Overwrite output file if already exists",
        default=False,
        required=False,
    )

    parser.add_argument(
        "--bounding_box",
        help="Derive bounding box from a different shapefile. Useful for "
        "putting multiple caves on a single map",
    )

    parser.add_argument(
        "--inset_x1",
        help="Starting point for inset, expressed as a % of width (0-100)",
        default=0,
        type=float,
    )

    parser.add_argument(
        "--inset_x2",
        help="Ending point for inset, expressed as a % of width (0-100)",
        default=100,
        type=float,
    )

    parser.add_argument(
        "--inset_y1",
        help="Starting point for inset, expressed as a % of height (0-100)",
        default=0,
        type=float,
    )

    parser.add_argument(
        "--inset_y2",
        help="Ending point for inset, expressed as a % of height (0-100)",
        default=100,
        type=float,
    )

    parser.add_argument(
        "--min_depth",
        help="Shallowest depth to include. More negative is deeper",
        default=float("inf"),
        type=float,
    )

    parser.add_argument(
        "--max_depth",
        help="Deepest depth to include. More negative is deeper",
        default=-float("inf"),
        type=float,
    )

    parser.add_argument(
        "-u",
        "--utm_zone",
        help="UTM zone for map projection",
        default=17,
        type=int,
    )

    parser.add_bool_argument(
        flag="-b",
        name="--use_border",
        help="Add a border around the image",
        default=False,
        required=False,
    )

    parser.add_argument(
        "--border_offset",
        help="Offset from edge to border, in inches",
        default=0.5,
        type=float,
    )

    parser.add_argument(
        "--width", help="Width of image in inches", default=36, type=float
    )

    parser.add_argument(
        "--height", help="Height of image in inches", default=24, type=float
    )

    parser.add_bool_argument(
        name="--use_depth_scale",
        help="Output a depth scale gradient",
        default=False,
        required=False,
    )

    parser.add_bool_argument(
        name="--debug",
        help="Show debug logs",
        default=False,
        required=False,
    )

    args = parser.parse_args()

    if args.debug:
        logger.logging.setLevel(logger.DEBUG)
        logger.logging.debug("Debug Logs Activated ...")

    runner = Runner(
        input_f=args.input_f,
        output_f=args.output_f,
        overwrite_if_exists=args.overwrite_if_exists,
        bounding_box=args.bounding_box,
        inset_x1=args.inset_x1,
        inset_x2=args.inset_x2,
        inset_y1=args.inset_y1,
        inset_y2=args.inset_y2,
        min_depth=args.min_depth,
        max_depth=args.max_depth,
        use_depth_scale=args.use_depth_scale,
        utm_zone=args.utm_zone,
        use_border=args.use_border,
        border_offset=args.border_offset,
        img_width=args.width,
        img_height=args.height,
    )

    runner.convert()
