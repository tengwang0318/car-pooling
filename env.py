import os
from collections import defaultdict
import h3
import osmnx as ox
import random

random.seed(64)
ENV = {
    "RESOLUTION": 8,
    "map_name": "chengdu.graphml",
    "time": 60,
    "money_per_meter": 0.005,
    "min_lng": 102.989623 + 0.2,
    "max_lng": 104.8948475 - 0.2,
    "min_lat": 30.09155 + 0.2,
    "max_lat": 31.4370968 - 0.2,
    "data_path": "data/data20161101/order_20161101_final.csv",
    "car_sharing_rate": 1,
    "velocity": 15,
    "split_size": 30,
    "number_of_neighbors": 6,
    "vehicle_number": 2000
}
LP_PATH = f"lp/RESOLUTION_{ENV['RESOLUTION']}_TIME_{ENV['time']}"
os.makedirs(LP_PATH, exist_ok=True)
LP_CNT = 1


def lp_filepath():
    global LP_CNT
    lp_path = os.path.join(LP_PATH, f"{LP_CNT}.lp")
    os.makedirs(os.path.join(LP_PATH, "log"), exist_ok=True)
    os.makedirs(os.path.join(LP_PATH, "data"), exist_ok=True)
    os.makedirs(os.path.join(LP_PATH, "solutions"), exist_ok=True)

    log_path = os.path.join(LP_PATH, "log", f"{LP_CNT}.log")
    data_path = os.path.join(LP_PATH, "data", f"{LP_CNT}.json")
    solution_path = os.path.join(LP_PATH, "solutions", f"solution_{LP_CNT}.json")

    LP_CNT += 1
    return lp_path, log_path, data_path, solution_path


coord_2_graph_idx = dict()
graph_idx_2_coord = dict()
G = ox.load_graphml(f"data/maps/{ENV['map_name']}")
gdf_nodes = ox.graph_to_gdfs(G, nodes=True, edges=False)

USERS_IN_REGION = defaultdict(set)

for node_id, row in gdf_nodes.iterrows():
    lat = row['y']
    lon = row['x']
    coord_2_graph_idx[(lat, lon)] = node_id
    graph_idx_2_coord[node_id] = (lat, lon)
    temp_idx = h3.geo_to_h3(lat, lon, resolution=ENV["RESOLUTION"])
    if temp_idx not in USERS_IN_REGION:  # it looks like scan the whole sub area
        USERS_IN_REGION[temp_idx] = set()

nodes_lon, nodes_lat = gdf_nodes['x'].tolist(), gdf_nodes['y'].tolist()
idx_dic = defaultdict(list)
for lat, lon in zip(nodes_lat, nodes_lon):
    idx = h3.geo_to_h3(lat, lon, ENV["RESOLUTION"])
    idx_dic[idx].append((lat, lon))
max_longitude, min_longitude = max(nodes_lon), min(nodes_lon)
max_latitude, min_latitude = max(nodes_lat), min(nodes_lat)

USERS = defaultdict(dict)
VEHICLES = dict()

EMPTY_VEHICLES = set()
FULL_CAPACITY_VEHICLES = set()
PARTIAL_CAPACITY_VEHICLES = set()
IDLE_VEHICLES = set()

EMPTY_VEHICLES_IN_REGION = defaultdict(set)
IDLE_VEHICLES_IN_REGION = defaultdict(set)
FULL_CAPACITY_VEHICLES_IN_REGION = defaultdict(set)
PARTIAL_CAPACITY_VEHICLES_IN_REGION = defaultdict(set)
