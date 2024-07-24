import heapq

import h3
from geopy.distance import geodesic
from env import coord_2_graph_idx, G
import networkx as nx


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
        idxes = h3.hex_ring(current_idx, k)
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


def find_nearest_node_except_specific_node(start_lat, start_lon, end_lat, end_lon, idx_dic: dict[str, list],
                                           resolution: int, visited: set):
    current_idx = h3.geo_to_h3(start_lat, start_lon, resolution)
    end_node = coord_2_graph_idx[(end_lat, end_lon)]

    pq = []

    k = 1

    while True:
        idxes = h3.hex_ring(current_idx, k)
        for idx in idxes:
            if idx in idx_dic:
                for temp_lat, temp_lon in idx_dic[idx]:
                    temp_distance = geodesic((temp_lat, temp_lon), (end_lat, end_lon)).meters
                    temp_node = coord_2_graph_idx[(temp_lat, temp_lon)]
                    if temp_node not in visited:
                        visited.add(temp_node)
                        heapq.heappush((temp_distance, temp_lat, temp_lon))
        while pq:
            temp_distance, temp_lat, temp_lon = heapq.heappop(pq)
            try:
                temp_node = coord_2_graph_idx[(temp_lat, temp_lon)]
                nx.shortest_path(G, temp_node, end_node, weight="length")
                return temp_node, temp_lat, temp_lon
            except:
                continue
        k += 1
