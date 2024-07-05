import h3
from geopy.distance import geodesic
import osmnx as ox
from env import coord_2_graph_idx


def find_nearest_node(lat, lon, idx_dic: dict[str, list], resolution):
    """
    Find the nearest node to the given latitude and longitude using H3 indexing.

    :param lat: Latitude of the point to search from.
    :param lon: Longitude of the point to search from.
    :param idx_dic: A dictionary where the key is an H3 index (string) and the value is a list of (lat, lon) tuples.
    :param resolution: Resolution level of the H3 index.
    :return: The latitude and longitude of the nearest node.
    """
    current_idx = h3.geo_to_h3(lat, lon, resolution)
    k = 0
    min_distance = float("inf")
    min_lat = None
    min_lon = None

    while True:
        idxes = h3.k_ring(current_idx, k)
        found = False
        for idx in idxes:
            if idx in idx_dic:
                for temp_lat, temp_lon in idx_dic[idx]:
                    temp_distance = geodesic((temp_lat, temp_lon), (lat, lon)).meters
                    if temp_distance < min_distance:
                        min_distance = temp_distance
                        min_lat = temp_lat
                        min_lon = temp_lon
                        found = True
        if found:
            break
        k += 1

    return coord_2_graph_idx[(min_lat, min_lon)]
