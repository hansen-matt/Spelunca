#!/usr/bin/python3

import logging
import os
import pathlib
import tempfile
import zipfile

import numpy as np
import pyproj
import shapefile
import svgwrite
from svgwrite import inch
from svgwrite import mm
from svgwrite.extensions import Inkscape

from src.logger import logging
from src.runner_utils import find_depth_limits
from src.runner_utils import make_depth_scale
from src.runner_utils import make_polygon_list


class Runner(object):
    def __init__(
        self,
        input_f,
        output_f,
        overwrite_if_exists,
        bounding_box,
        inset_x1,
        inset_x2,
        inset_y1,
        inset_y2,
        min_depth,
        max_depth,
        use_depth_scale,
        utm_zone,
        use_border,
        border_offset,
        img_width,
        img_height,
    ):
        self._input_f = pathlib.Path(input_f)
        self._output_f = pathlib.Path(output_f)
        self._overwrite_if_exists = overwrite_if_exists
        self._bounding_box = bounding_box
        self._inset_x1 = inset_x1
        self._inset_x2 = inset_x2
        self._inset_y1 = inset_y1
        self._inset_y2 = inset_y2
        self._min_depth = min_depth
        self._max_depth = max_depth
        self._use_depth_scale = use_depth_scale
        self._utm_zone = utm_zone
        self._use_border = use_border
        self._border_offset = border_offset
        self._img_width = img_width
        self._img_height = img_height

        # 1. Validating IO Paths
        logging.debug("Validating Paths ...")

        if not self._input_f.exists():
            raise FileNotFoundError(f"File `{self._input_f}` not found ...")

        if self._output_f.exists():
            if not self._overwrite_if_exists:
                raise FileExistsError(
                    f"File `{self._output_f}` already exists. Use "
                    "`--overwrite_if_exists` to overwrite."
                )
            else:
                self._output_f.unlink()  # delete file

        # Ensuring output directory exists.
        self._output_f.parent.mkdir(parents=True, exist_ok=True)

        # 2. Defining BBOX
        logging.debug("Defining BBOX ...")
        if self._bounding_box:
            self._bbox_path = self._bounding_box
        else:
            self._bbox_path = self._input_f

    def _create_border(self, svg_document, inkscape):
        logging.debug("Creating Inkspace Border ...")

        border_layer = inkscape.layer(label="border", locked=True)
        svg_document.add(border_layer)

        border_offset = self._border_offset

        border = svg_document.rect(
            (border_offset * inch, border_offset * inch),
            (
                (self._img_width - 2 * border_offset) * inch,
                (self._img_height - 2 * border_offset) * inch,
            ),
            fill="none",
            stroke="black",
            stroke_width=1 * mm,
        )

        border_layer.add(border)

    def _extract_input_f(self):
        temp_dir = tempfile.mkdtemp()
        logging.debug(f"Extracting `{self._input_f=}` to `{temp_dir=}`")

        with zipfile.ZipFile(self._input_f, "r") as zip_file:
            zip_file.extractall(temp_dir)

        return temp_dir

    def convert(self):
        # Set limits for x,y
        min_x = self._inset_x1 * self._img_width
        min_y = self._inset_y1 * self._img_height
        max_x = self._inset_x2 * self._img_width
        max_y = self._inset_y2 * self._img_height

        logging.debug("*******************************************************")
        logging.debug(f"\t- {min_x=}")
        logging.debug(f"\t- {min_y=}")
        logging.debug(f"\t- {max_x=}")
        logging.debug(f"\t- {max_y=}")
        logging.debug("*******************************************************")

        # Create an SVG drawing
        svg_document = svgwrite.Drawing(
            self._output_f,
            profile="tiny",
            size=(self._img_width * inch, self._img_height * inch),
        )
        inkscape = Inkscape(svg_document)

        # Add a border
        if self._use_border:
            self._create_border(svg_document, inkscape)

        # Add a layer for the map
        map_layer = inkscape.layer(label="depth_map", locked=True)
        svg_document.add(map_layer)

        # --------------------- Figure out the projection -------------------- #

        # First, unzip the zip file to a temp directory
        temp_dir = self._extract_input_f()

        basename = os.path.basename(self._input_f)
        prj_path = temp_dir + "/" + basename.replace("zip", "prj")

        # Define the UTM projection suitable for your area of interest
        with open(prj_path, "r") as f:
            inProj = pyproj.Proj(f.read())

        outProj = pyproj.Proj(f"EPSG:326{self._utm_zone}")
        projector = pyproj.Transformer.from_proj(inProj, outProj)

        # Define the scale factor for 30 feet = 1 inch
        scale_factor = 12.0 * 2.54 / (30.0)  # Convert 30 feet to cm

        # y is north up, PNG is positive down, so invert
        scale_factor_xy = [scale_factor, -1 * scale_factor]

        # Find the bounding box and offset
        shallowest = -float("inf")
        deepest = float("inf")

        try:
            with shapefile.Reader(self._bbox_path) as shape:
                bbox = [
                    (shape.bbox[0], shape.bbox[2], shape.zbox[0]),
                    (shape.bbox[1], shape.bbox[3], shape.zbox[1]),
                ]
                transformed_bbox = [
                    projector.transform(x, y) for x, y, z in bbox
                ]
                scaled_bbox = np.multiply(transformed_bbox, scale_factor_xy)

                # get the min x, and what would have been the max y,
                # because y is inverted with the scale factor so max is min
                bbox_offset = [scaled_bbox[0][0] - 200, scaled_bbox[1][1] - 400]

                # colors for depth
                shallowest, deepest = find_depth_limits(
                    shape=shape,
                    shapefile=shapefile,
                    shallowest=shallowest,
                    deepest=deepest,
                )

        except shapefile.ShapefileException as e:
            print(f"Error processing shapefile: {str(e)}")

        if self._use_depth_scale:
            make_depth_scale(
                svg_document, map_layer, min_depth=shallowest, max_depth=deepest
            )

        else:
            # Process the passages in the shapefile into polygons
            try:
                with shapefile.Reader(self._input_f) as shape:
                    polygon_list = make_polygon_list(
                        shape,
                        svg_document,
                        projector,
                        scale_factor_xy,
                        bbox_offset,
                        min_x,
                        max_x,
                        min_y,
                        max_y,
                        max_depth=deepest,
                    )

                    for polygon_depth in polygon_list:
                        polygon = polygon_depth[1]
                        map_layer.add(polygon)

            except shapefile.ShapefileException as e:
                print(f"Error processing shapefile: {str(e)}")

        print(f"Minimum depth: {shallowest}")
        print(f"Maximum depth: {deepest}")

        # Save the SVG file
        svg_document.save()
        print(f"SVG file saved to `{self._output_f}`")
