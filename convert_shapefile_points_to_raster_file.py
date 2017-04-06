#! /usr/bin/python3

import sys

import shapefile
import numpy as np
from matplotlib import pyplot as plt
import rasterio
from rasterio.transform import from_origin
from rasterio.transform import rowcol


def read_shapefile(path, attribute_name):
    sf = shapefile.Reader(path)
    westsoutheastnorth = sf.bbox
    field_names = [e[0] for e in sf.fields[1:]]
    attribute_index = field_names.index(attribute_name)
    shape_records = [(shape_record.shape.points[0],
        shape_record.record[attribute_index]) for shape_record in
        sf.shapeRecords()]
    return westsoutheastnorth, shape_records


def draw_marker(raster_map, row, col, val):
    raster_map[row - 1, col - 1] = val
    raster_map[row, col - 1] = val
    raster_map[row + 1, col - 1] = val
    raster_map[row - 1, col] = val
    raster_map[row, col] = val
    raster_map[row + 1, col] = val
    raster_map[row - 1, col + 1] = val
    raster_map[row, col + 1] = val
    raster_map[row + 1, col + 1] = val


def scale_value(val, _min, _max):
    "from any range to 0-255"
    return 255 * (val - _min) / (_max - _min)


def draw_map(shape_records, westsoutheastnorth, resolution):
    west, south, east, north = westsoutheastnorth
    x_size_raster = int(abs(west - east) * resolution) + 1
    y_size_raster = int(abs(north - south) * resolution) + 1
    raster_map = np.zeros((x_size_raster, y_size_raster), np.uint8)
    west, south, east, north = westsoutheastnorth
    x_size_transform = abs(west - east) / raster_map.shape[1]
    y_size_transform = abs(north - south) / raster_map.shape[0]
    transform = from_origin(west, north, x_size_transform, y_size_transform)
    _min = min(shape_records)
    _max = max(shape_records)
    for shape_record in shape_records:
        lat, lon = shape_record[0]
        row, col = rowcol(transform, lat, lon)
        if col == raster_map.shape[1]:
            col -= 2
        if row == raster_map.shape[0]:
            row -= 2
        val = scale_value(shape_record[1], _min, _max)
        draw_marker(raster_map, row, col, val)
    return transform, raster_map


def get_colormap():
    colormap = {}
    for grayscale in range(256):
        colormap[grayscale] = (grayscale, grayscale, grayscale)
    return colormap


def save_transformed_map(path, raster_map, transform):
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
    print(raster_map.max())
    print(raster_map.min())
    plt.imshow(np.transpose(raster_map), cmap="hot")
    plt.show()


def main(path_in, path_out, attribute_name, resolution):
    westsoutheastnorth, shape_records = read_shapefile(path_in, attribute_name)
    transform, raster_map = draw_map(shape_records, westsoutheastnorth,
        resolution)
    save_transformed_map(path_out, raster_map, transform)


if __name__ == "__main__":
    main(*sys.argv[1:])
