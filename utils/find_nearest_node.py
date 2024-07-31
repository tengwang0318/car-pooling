import heapq

import h3
from geopy.distance import geodesic
from env import coord_2_graph_idx, G, graph_idx_2_coord, ENV
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


def find_nearest_node_except_specific_node(start_lat, start_lon, start_node, end_lat, end_lon, end_node,
                                           idx_dic: dict[str, list], resolution: int):
    current_idx = h3.geo_to_h3(start_lat, start_lon, resolution)
    end_lat, end_lon = graph_idx_2_coord[end_node]
    pq = []
    k = 1

    while True:
        idxes = h3.hex_ring(current_idx, k)
        for idx in idxes:
            if idx in idx_dic:
                for temp_lat, temp_lon in idx_dic[idx]:
                    temp_distance = geodesic((temp_lat, temp_lon), (end_lat, end_lon)).meters
                    heapq.heappush(pq, (temp_distance, temp_lat, temp_lon))
        while pq:
            temp_distance, temp_lat, temp_lon = heapq.heappop(pq)
            try:
                temp_node = coord_2_graph_idx[(temp_lat, temp_lon)]
                nx.shortest_path(G, temp_node, end_node, weight="length")
                return temp_node, temp_lat, temp_lon, end_node, end_lat, end_lon
            except:
                continue
        k += 1
        print(f"k=={k}")
        if k == 10:
            break

    current_idx = h3.geo_to_h3(end_lat, end_lon, resolution)
    start_lat, start_lon = graph_idx_2_coord[start_node]
    pq = []
    k = 1
    while True:
        idxes = h3.hex_ring(current_idx, k)
        for idx in idxes:
            if idx in idx_dic:
                for temp_lat, temp_lon in idx_dic[idx]:
                    temp_distance = geodesic((temp_lat, temp_lon), (start_lat, start_lon)).meters
                    heapq.heappush(pq, (temp_distance, temp_lat, temp_lon))
        while pq:
            temp_distance, temp_lat, temp_lon = heapq.heappop(pq)
            try:
                temp_node = coord_2_graph_idx[(temp_lat, temp_lon)]
                nx.shortest_path(G, temp_node, start_node, weight="length")
                return start_node, start_lat, start_lon, temp_node, temp_lat, temp_lon
            except:
                continue
        k += 1
        print(f"2_k=={k}")
        if k == 10:
            break
    print("fuck!!!")
    start_lon, start_lat, end_lon, end_lat = 104.09197, 30.66158, 104.13081, 30.63761
    start_node = find_nearest_node(lat=start_lat, lon=start_lon, idx_dic=idx_dic, resolution=resolution)
    end_node = find_nearest_node(lat=end_lat, lon=end_lon, idx_dic=idx_dic, resolution=resolution)

    return start_node, start_lat, start_lon, end_node, end_lat, end_lon
