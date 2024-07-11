from collections import defaultdict
import h3
import osmnx as ox

ENV = {
    "RESOLUTION": 10,
    "map_name": "chengdu.graphml",
    "time": 60,
    "money_per_meter": 0.005,
    "min_lng": 102.989623,
    "max_lng": 104.8948475,
    "min_lat": 30.09155,
    "max_lat": 31.4370968,
    "data_path": "data/data20161101/order_20161101_final.csv",
    "car_sharing_rate": 0.6
}
coord_2_graph_idx = dict()
graph_idx_2_coord = dict()
G = ox.load_graphml(f"data/maps/{ENV['map_name']}")
gdf_nodes = ox.graph_to_gdfs(G, nodes=True, edges=False)
for node_id, row in gdf_nodes.iterrows():
    lat = row['y']
    lon = row['x']
    coord_2_graph_idx[(lat, lon)] = node_id
    graph_idx_2_coord[node_id] = (lat, lon)

nodes_lon, nodes_lat = gdf_nodes['x'].tolist(), gdf_nodes['y'].tolist()
idx_dic = defaultdict(list)
for lat, lon in zip(nodes_lat, nodes_lon):
    idx = h3.geo_to_h3(lat, lon, ENV["RESOLUTION"])
    idx_dic[idx].append((lat, lon))
max_longitude, min_longitude = max(nodes_lon), min(nodes_lon)
max_latitude, min_latitude = max(nodes_lat), min(nodes_lat)
USERS = dict()
VEHICLES = dict()


EMPTY_VEHICLES = set()
FULL_CAPACITY_VEHICLES = set()
PARTIAL_CAPACITY_VEHICLES = set()
IDLE_VEHICLES = set()


