from unittest import TestCase
from mtsgo.geocalc import *

class GeospatialCalculationTest(TestCase):

    def setUp(self):
        pass

    def test_calculate_distance(self):
        p1 = tuple([48.2155, -4.0553, 0])
        p2 = tuple([48.1129, -3.5664, 0])
        self.assertAlmostEqual(geo_distance_between_points(p1,p2), 55542.2868377345)


    def test_point_in_polygon(self):
        p1 = tuple([48.2251, -3.8735, 0])
        p2 = tuple([48.196, -3.8371, 0])
        p3 = tuple([48.2005, -3.9015, 0])
        p_true = tuple([48.215, -3.8742, 0])
        p_false = tuple([28.215, -9.8742, 0])
        self.assertTrue(geo_point_in_polygon(p_true, [p1,p2,p3]))
        self.assertFalse(geo_point_in_polygon(p_false, [p1,p2,p3]))
