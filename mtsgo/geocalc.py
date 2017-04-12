# -*- coding: utf8 -*-
from math import radians, cos, sin, asin, sqrt
import numpy as np
import matplotlib.path as mplPath

def geo_distance_between_points(p1, p2):
    """
     Calcule la distance entre deux points de la terre (spécifiés en degrés décimaux)[#]_
     **Note: ** Shamelessly stolen from http://stackoverflow.com/a/4913653
    :param p1: Premier point.
    :param p2: L'autre point.
    :return: La distance en mètres.
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [p1[0], p1[1], p2[0], p2[1]])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371008  # Radius of earth in meters.
    return c * r


def geo_point_in_polygon(point, poly):
    """
    Vérifie si un point est dans un polygone.
    **Note :** On travaille dans l'approximation du Campus. Hors de cette approximation, la validité de cet
    algorithme n'est pas garantie.
    :param point: Point décrit par un tuple de deux à trois float.
    :param poly: List de Points décrivant les arrêts du polygone.
    :return: True si le point appartient au polygone, False sinon.
    """
    poly = np.array([np.array([p[0], p[1]]) for p in poly])
    mPath = mplPath.Path(poly)
    return mPath.contains_point((point[0], point[1]))
