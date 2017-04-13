#! /usr/env python

"""
inspired by https://gis.stackexchange.com/questions/235165

Values are in SI values, meaning meters, degrees, ...
"""
import unittest
from math import pi, cos

# in meter
EARTH_RADIUS = 6371009


def calculate_distance_difference(north_degree, west_degree, south_degree, east_degree):
    """
    Calculates the distance at the northern and southern border of the map
    assuming that the earth has a spherical shape
    
    Provide all values in degrees.
    """
    delta_east_west_radians = abs(west_degree - east_degree) * pi / 180
    north_radians = north_degree * pi / 180
    south_radians = south_degree * pi / 180
    distance_north = EARTH_RADIUS * cos(north_radians) * delta_east_west_radians
    distance_south = EARTH_RADIUS * cos(south_radians) * delta_east_west_radians
    return distance_north, distance_south


class Test(unittest.TestCase):

    def test_calculate_distance_difference(self):
        north = 54.3460005
        west = 10.1494873
        south = 54.2984447
        east = 10.2002991
        d_north, d_south = calculate_distance_difference(north, west, south, east)
        self.assertAlmostEqual(d_north, 3293.3, 1)
        self.assertAlmostEqual(d_south, 3297.1, 1)
