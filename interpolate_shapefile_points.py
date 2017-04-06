#! /usr/bin/python3

"""
This file takes a shapefile and rasterizes it. Only geometric points are
supported. This is a preliminary work for the interpolation idea.

this script can be called like this

    convert_shapefile_points_to_raster_file <SHAPEFILE> <TIF-IMG> <ATTR> <INT>


"""

import sys

import numpy as np
from rasterio.transform import from_origin
from rasterio.transform import rowcol
from affine import Affine

from convert_shapefile_points_to_raster_file import *
from scipy.interpolate import griddata


def draw_interpolated_map(shape_records, westsoutheastnorth, resolution):
    """draws shape records on map"""
    west, south, east, north = westsoutheastnorth
    buffer_around = int(resolution / 30)
    x_size_raster = int(abs(west - east) * resolution)
    y_size_raster = int(abs(north - south) * resolution)
    raster_map = np.zeros((y_size_raster + buffer_around, x_size_raster + buffer_around))
    x_size_transform = abs(west - east) / x_size_raster
    y_size_transform = abs(north - south) / y_size_raster
    transform = (from_origin(west, north, x_size_transform, y_size_transform)
        * Affine.translation(-buffer_around / 2, -buffer_around / 2))
    coords = np.array([rowcol(transform, s[0][0], s[0][1]) for s in shape_records])
    attributes = [s[1] for s in shape_records]
    _min, _max = min(attributes), max(attributes)
    attributes = [scale_value(val, _min, _max) for val in attributes]
    grid_x, grid_y = np.mgrid[0:raster_map.shape[0], 0:raster_map.shape[1]]
    raster_map = griddata(coords, attributes, (grid_x, grid_y), fill_value=0)  #, method="nearest"
    print(raster_map.shape, raster_map.max(), raster_map.min())
    for shape_record in shape_records:
        lat, lon = shape_record[0]
        row, col = rowcol(transform, lat, lon)
        val = scale_value(shape_record[1], _min, _max)
        draw_marker(raster_map, row, col, val, resolution, 0)
    return transform, raster_map


def main(path_in, path_out, attribute_name, resolution):
    """combine upper methods and run all together"""
    westsoutheastnorth, shape_records = read_shapefile(path_in, attribute_name)
    transform, raster_map = draw_interpolated_map(shape_records, westsoutheastnorth, resolution)
    #save_raster_map(path_out, raster_map, transform)
    show_map(raster_map)


if __name__ == "__main__":
    path_in = sys.argv[1]
    path_out = sys.argv[2]
    attribute_name = sys.argv[3]
    resolution = int(sys.argv[4])
    main(path_in, path_out, attribute_name, resolution)
