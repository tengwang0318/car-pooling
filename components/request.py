import networkx as nx
import osmnx as ox
from utils.find_nearest_node import find_nearest_node
from env import ENV, idx_dic


class Request:
    def __init__(self,
                 start_longitude: float,
                 start_latitude: float,
                 end_longitude: float,
                 end_latitude: float,
                 G,
                 enable_share: bool,
                 ):
        self.start_longitude = start_longitude
        self.start_latitude = start_latitude
        self.end_longitude = end_longitude
        self.end_latitude = end_latitude

        self.start_node = find_nearest_node(lat=start_latitude, lon=start_longitude, idx_dic=idx_dic,
                                            resolution=ENV["resolution"])
        self.end_node = find_nearest_node(lat=end_latitude, lon=end_longitude, idx_dic=idx_dic,
                                          resolution=ENV["resolution"])
        self.G = G
        self.path_list = nx.shortest_path(self.G, self.start_node, self.end_node, weight="length")
        route_gdf = ox.routing.route_to_gdf(self.G, self.path_list)
        self.distance_list = list(route_gdf['length'])

        self.enable_share = enable_share


