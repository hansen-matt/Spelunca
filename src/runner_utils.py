#!/usr/bin/python3

import math

import matplotlib.pyplot as plt
import numpy as np
import shapefile

from src.logger import logging


def find_depth_limits(shape, shapefile, shallowest, deepest):
    for shape_record in iter(shape):
        geometry = shape_record.shape

        if geometry.shapeType == shapefile.POLYGONZ:
            points_z = geometry.z
            min_depth = np.min(points_z)
            max_depth = np.max(points_z)
            shallowest = max(shallowest, min_depth)
            deepest = min(deepest, max_depth)

    logging.debug("*******************************************************")
    logging.debug(f"\t- {shallowest=}")
    logging.debug(f"\t- {deepest=}")
    logging.debug("*******************************************************")

    return shallowest, deepest


# Colormap related functions
def rgb_to_hex(rgb):
    rgb = np.round(np.multiply(rgb, 256))
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def get_color(depth, max_depth):
    depth_color = plt.cm.Blues_r
    depth_norm = plt.Normalize(vmin=10 * math.floor(max_depth / 10), vmax=0)

    fill_color = depth_color(depth_norm(depth))
    hex_color = rgb_to_hex(fill_color)
    return hex_color


def make_depth_scale(svg_document, map_layer, min_depth, max_depth):
    logging.debug("Creating Depth Scale ...")
    depth_step = (max_depth - min_depth) / 1000

    for x in range(0, 1000):
        offset_xy = [[x, 0], [x, 100], [x + 2, 100], [x + 2, 0], [x, 0]]

        depth = min_depth + x * depth_step

        polygon = make_polygon(
            svg_document, offset_xy, color=get_color(depth, max_depth=max_depth)
        )

        map_layer.add(polygon)


# Functions to check if all the elements in a tuple are valid
def is_finite_list_of_tuples(tuple_list):
    return all([math.isfinite(el) for tpl in tuple_list for el in tpl])


def scaled_xy_is_good(scaled_xy):
    return scaled_xy.all() and is_finite_list_of_tuples(scaled_xy)


def should_make_polygon(
    offset_xy, points_z, min_x, max_x, min_y, max_y, min_depth, max_depth
):
    x, y = zip(*offset_xy)

    min_depth = np.min(points_z)
    max_depth = np.max(points_z)

    if np.min(x) < min_x or np.max(x) > max_x:
        return False

    if np.min(y) < min_y or np.max(y) > max_y:
        return False

    if min_depth > min_depth or max_depth < max_depth:
        return False

    return True


def make_polygon(svg_document, offset_xy, color):
    polygon = svg_document.polygon(
        points=offset_xy, fill=color
    )  # , stroke='none', stroke_width=0.0*mm)
    return polygon


def make_polygon_list(
    shape,
    svg_document,
    projector,
    scale_factor_xy,
    bbox_offset,
    min_x,
    max_x,
    min_y,
    max_y,
    max_depth,
):
    polygon_list = []
    # Loop through shapefile records
    for shape_record in shape.iterShapeRecords():
        # Extract the geometry
        geometry = shape_record.shape

        # Handle 3D polygons (shapefile.POLYGONZ). Ignore the Z-coordinate for projection, but use it for color
        if geometry.shapeType == shapefile.POLYGONZ:
            for part in geometry.parts:
                points_xy = geometry.points  # [part:part + geometry.parts[0]]
                points_z = geometry.z

                min_depth = np.min(points_z)

                projected_xy = [projector.transform(x, y) for x, y in points_xy]
                scaled_xy = np.multiply(projected_xy, scale_factor_xy)

                offset_xy = np.subtract(scaled_xy, bbox_offset)

                if scaled_xy_is_good(scaled_xy):
                    # if should_make_polygon(offset_xy, points_z):
                    if should_make_polygon(
                        offset_xy,
                        points_z,
                        min_x,
                        max_x,
                        min_y,
                        max_y,
                        min_depth,
                        max_depth,
                    ):
                        polygon = make_polygon(
                            svg_document,
                            offset_xy,
                            color=get_color(min_depth, max_depth=max_depth),
                        )

                        polygon_list.append((min_depth, polygon))

    polygon_list.sort(key=lambda a: a[0])
    return polygon_list
