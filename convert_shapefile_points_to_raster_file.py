#! /usr/bin/python3

"""
This file takes a shapefile and rasterizes it. Only geometric points are
supported. This is a preliminary work for the interpolation idea.

this script can be called like this

    convert_shapefile_points_to_raster_file <SHAPEFILE> <TIF-IMG> <ATTR> <INT>


"""

import sys

import shapefile
import numpy as np
from matplotlib import pyplot as plt
import rasterio
from rasterio.transform import from_origin
from rasterio.transform import rowcol
from skimage import draw
from affine import Affine


def read_shapefile(path, attribute_name):
    """read coordinates and attributes from shapefile"""
    sf = shapefile.Reader(path)
    westsoutheastnorth = sf.bbox
    field_names = [e[0] for e in sf.fields[1:]]
    attribute_index = field_names.index(attribute_name)
    shape_records = [(shape_record.shape.points[0],
        shape_record.record[attribute_index]) for shape_record in
        sf.shapeRecords()]
    return westsoutheastnorth, shape_records


def draw_marker(raster_map, row, col, val, resolution, border_intensity):
    """draw marker on raster_map"""
    row_area, col_area = draw.circle(row, col, radius=resolution / 200,
        shape=raster_map.shape)
    raster_map[row_area, col_area] = border_intensity
    row_area, col_area = draw.circle(row, col, radius=resolution / 300,
        shape=raster_map.shape)
    raster_map[row_area, col_area] = val


def scale_value(val, _min, _max):
    """scale from any range to 0-255 in order to use the full range"""
    return 255 * (val - _min) / (_max - _min)


def draw_map(shape_records, westsoutheastnorth, resolution):
    """draws shape records on map"""
    west, south, east, north = westsoutheastnorth
    buffer_around = int(resolution / 30)
    x_size_raster = int(abs(west - east) * resolution)
    y_size_raster = int(abs(north - south) * resolution)
    raster_map = np.zeros((y_size_raster + buffer_around,
        x_size_raster + buffer_around), np.uint8)
    x_size_transform = abs(west - east) / x_size_raster
    y_size_transform = abs(north - south) / y_size_raster
    transform = (from_origin(west, north, x_size_transform, y_size_transform)
        * Affine.translation(-buffer_around / 2, -buffer_around / 2))
    attributes = [s[1] for s in shape_records]
    _min = min(attributes)
    _max = max(attributes)
    for shape_record in shape_records:
        lat, lon = shape_record[0]
        row, col = rowcol(transform, lat, lon)
        val = scale_value(shape_record[1], _min, _max)
        draw_marker(raster_map, row, col, val, resolution, _max)
    return transform, raster_map


def get_colormap():
    """TIF files need a color map"""
    colormap = {}
    for intensity in range(256):
        grayscale = 255 - intensity
        colormap[intensity] = (grayscale, grayscale, grayscale)
    return colormap


def save_raster_map(path, raster_map, transform):
    """saves map in project standard crs"""
    with rasterio.open(path, 'w', driver='GTiff',
        height=raster_map.shape[0], width=raster_map.shape[1], count=1,
        dtype=raster_map.dtype, crs='EPSG:4326',
        transform=transform) as new_dataset:
        new_dataset.write(raster_map, 1)
        new_dataset.write_colormap(
            1,
            get_colormap()
        )


def show_map(raster_map):
    """shows map for visual inspection"""
    plt.imshow(raster_map, cmap="hot")
    plt.show()


def main(path_in, path_out, attribute_name, resolution):
    """combine upper methods and run all together"""
    westsoutheastnorth, shape_records = read_shapefile(path_in, attribute_name)
    transform, raster_map = draw_map(shape_records, westsoutheastnorth,
        resolution)
    #save_raster_map(path_out, raster_map, transform)
    show_map(raster_map)


if __name__ == "__main__":
    path_in = sys.argv[1]
    path_out = sys.argv[2]
    attribute_name = sys.argv[3]
    resolution = int(sys.argv[4])
    main(path_in, path_out, attribute_name, resolution)
