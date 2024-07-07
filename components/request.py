import networkx as nx
import osmnx as ox
from utils.find_nearest_node import find_nearest_node
from env import ENV, idx_dic, G
from .user import User

ID = 0


class Request:
    def __init__(self,
                 start_longitude: float,
                 start_latitude: float,
                 end_longitude: float,
                 end_latitude: float,
                 enable_share: bool,
                 is_pickup_request: bool,
                 is_dropoff_request: bool,
                 users: list[User],
                 start_node=None,
                 end_node=None,
                 path_node_list=None,
                 ):
        global ID
        self.ID = ID
        ID += 1
        self.start_longitude = start_longitude
        self.start_latitude = start_latitude
        self.end_longitude = end_longitude
        self.end_latitude = end_latitude
        if start_node and end_node and path_node_list:
            self.start_node = start_node
            self.end_node = end_node
            self.path_node_list = path_node_list
        else:
            self.start_node = find_nearest_node(lat=start_latitude, lon=start_longitude, idx_dic=idx_dic,
                                                resolution=ENV["RESOLUTION"])
            self.end_node = find_nearest_node(lat=end_latitude, lon=end_longitude, idx_dic=idx_dic,
                                              resolution=ENV["RESOLUTION"])
            self.path_node_list = nx.shortest_path(G, self.start_node, self.end_node, weight="length")  # 可能no path， 需要考虑下

        route_gdf = ox.routing.route_to_gdf(G, self.path_node_list)
        self.path_distance_list = list(route_gdf['length'])

        self.request_total_distance = sum(self.path_distance_list)

        self.enable_share = enable_share
        self.is_pickup_request = is_pickup_request
        self.is_dropoff_request = is_dropoff_request

        # 还没用到
        self.start_time = None
        self.end_time = None
        self.vehicle = None

        self.users = users
