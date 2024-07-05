from collections import defaultdict

import h3
import osmnx as ox
import networkx as nx

ENV = {
    "RESOLUTION": 10,
    "map_name": "chengdu.graphml",

}
G = ox.load_graphml(f"data/{ENV['map_name']}.graphml")
gdf_nodes = ox.graph_to_gdfs(G)
nodes_lon, nodes_lat = gdf_nodes['x'].tolist(), gdf_nodes['y'].tolist()

idx_dic = defaultdict(list)
for lat, lon in zip(nodes_lat, nodes_lon):
    idx = h3.geo_to_h3(lat, lon, ENV["RESOLUTION"])
    idx_dic[idx].append((lat, lon))
