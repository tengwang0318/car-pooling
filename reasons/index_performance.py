from collections import defaultdict
from geopy.distance import geodesic
import osmnx as ox
import h3
import time

resolution = 10

G = ox.graph_from_place('Manhattan, New York, USA', network_type='walk')
gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
nodes_lon, nodes_lat = gdf_nodes['x'].tolist(), gdf_nodes['y'].tolist()

idx_dic = defaultdict(list)
for lat, lon in zip(nodes_lat, nodes_lon):
    idx = h3.geo_to_h3(lat, lon, resolution)
    idx_dic[idx].append((lat, lon))

coordinates = [
    (40.748817, -73.985428),  # Empire State Building
    (40.712776, -74.005974),  # One World Trade Center
    (40.730610, -73.935242),  # Brooklyn
    (40.785091, -73.968285),  # Central Park
    (40.706192, -73.996864),  # Brooklyn Heights
    (40.851767, -73.935242),  # Bronx
    (40.641311, -73.778139),  # JFK Airport
    (40.689247, -74.044502),  # Statue of Liberty
    (40.742054, -73.769417),  # Queens
    (40.658062, -74.002089),  # Staten Island
    (40.578120, -74.156292),  # Tottenville, Staten Island (suburban area)
    (40.828224, -73.926300),  # Yankee Stadium, Bronx
    (40.702749, -73.808319),  # Jamaica, Queens
    (40.575545, -73.970702),  # Coney Island, Brooklyn
    (40.849850, -73.887382),  # Fordham, Bronx
    (40.720581, -73.844852),  # Flushing, Queens
    (40.905277, -73.901708),  # Riverdale, Bronx
    (40.663991, -73.938084),  # Brownsville, Brooklyn
    (40.768732, -73.964438),  # Upper East Side, Manhattan
    (40.756097, -73.986927),  # Times Square, Manhattan
    (40.916042, -73.744227)   # Pelham Bay, Bronx (suburban area)
]

def get_nearest_node(lat, lon, G):
    nearest_node = ox.distance.nearest_nodes(G, X=lon, Y=lat)
    return nearest_node

for lat, lon in coordinates:
    start_time = time.time()
    nearest_node_ox = get_nearest_node(lat, lon, G)
    end_time = time.time()
    time_ox = end_time - start_time
    nearest_node_lat = G.nodes[nearest_node_ox]['y']
    nearest_node_lon = G.nodes[nearest_node_ox]['x']

    print(f"Coordinates: ({lat}, {lon})")
    print(f"[osmnx] Nearest node: {nearest_node_ox}")
    print(f"[osmnx] Latitude: {nearest_node_lat}, Longitude: {nearest_node_lon}")
    print(f"[osmnx] Time taken: {time_ox:.6f} seconds\n")

    start_time = time.time()
    current_idx = h3.geo_to_h3(lat, lon, resolution)
    k = 1
    min_distance = float('inf')
    min_idx = None
    min_lat, min_lon = None, None

    while True:
        idxes = h3.k_ring(current_idx, k)
        for idx in idxes:
            if idx in idx_dic:
                for temp_lat, temp_lon in idx_dic[idx]:
                    temp_distance = geodesic((temp_lat, temp_lon), (lat, lon)).meters
                    if temp_distance < min_distance:
                        min_distance = temp_distance
                        min_idx = idx
                        min_lat, min_lon = temp_lat, temp_lon
        k += 1
        if min_idx is not None:
            break

    end_time = time.time()
    print(f"[H3] Nearest node latitude: {min_lat}, longitude: {min_lon}")
    print(f"[H3] Time taken: {end_time - start_time:.6f} seconds\n")
