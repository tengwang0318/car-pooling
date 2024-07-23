import osmnx as ox
import h3
import argparse

from env import *


def read_map(city: str = "NewYorkCity"):
    """
    Read the map and generate the node and edge
    """
    if city == "NewYorkCity":
        path = "data/maps/new_york_city.graphml"
    elif city == "ChengDu":
        path = "data/maps/chengdu.graphml"
    else:
        raise ValueError("City map doesn't exists")
    G = ox.load_graphml(path)
    nodes, edges = ox.graph_to_gdfs(G)

    return nodes, edges


def hex_to_coord(hex_index):
    lat, lon = h3.h3_to_geo(hex_index)
    return lat, lon


def get_the_boundary(nodes):
    """
    Get the latitude and longitude of boundary points and return formatted bounding box
    """
    north, south, east, west = nodes['y'].max(), nodes['y'].min(), nodes['x'].max(), nodes['x'].min()
    polygon = {
        'type': 'Polygon',
        'coordinates': [[
            [west, north],
            [east, north],
            [east, south],
            [west, south],
            [west, north]
        ]]
    }
    return polygon, south, north, west, east


def generate_hexagons(polygon, resolution):
    """
    Based on the resolution, return all of divided areas which is represented as hex number
    """
    hexagons = h3.polyfill(polygon, resolution)
    return hexagons


def find_hexagon(lat, lon, resolution):
    h3_index = h3.geo_to_h3(lat, lon, resolution)
    return h3_index


def find_nearby_hexagons(hex_index, k=1, min_lat=ENV["min_lat"], max_lat=ENV["max_lat"], min_lng=ENV["min_lng"],
                         max_lng=ENV["max_lng"]):
    """
    Find nearby hexagons for a given hexagon index within k distance.
    """
    nearby_hexagons = h3.k_ring(hex_index, k)
    filtered_hexagons = set()

    for h3_index in nearby_hexagons:
        lat, lng = h3.h3_to_geo(h3_index)
        if min_lat <= lat <= max_lat and min_lng <= lng <= max_lng:
            filtered_hexagons.add(h3_index)

    return filtered_hexagons


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resolution', type=int, default=10)
    parser.add_argument("--city", type=str, default="NewYorkCity")

    args = parser.parse_args()
    nodes, edges = read_map(args.city)
    polygon, south, north, west, east = get_the_boundary(nodes)
    print(north, south, west, east)
    test_lat = 40.7831
    test_lon = -73.9712
    hex_index = find_hexagon(test_lat, test_lon, args.resolution)
    print(f"The H3 index for ({test_lat, test_lon}) is {hex_index}")
    # Find nearby hexagons
    nearby_hexagons = find_nearby_hexagons(hex_index, k=1, min_lat=south, max_lat=north, min_lng=west, max_lng=east)
    print(f"The nearby H3 indices within bounds for index {hex_index} are: {nearby_hexagons}")


if __name__ == '__main__':
    main()
