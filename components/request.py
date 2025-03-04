import networkx as nx
import osmnx as ox
from utils.find_nearest_node import find_nearest_node, find_nearest_node_except_specific_node
from env import ENV, idx_dic, G, graph_idx_2_coord
from .user import User

ID = 0


class Request:
    def __init__(self,
                 enable_share: bool,
                 # the default value of pickup request is True, drop off request depends on user's willing
                 is_pickup_request: bool,
                 is_dropoff_request: bool,
                 users: list[User],
                 start_longitude: float = None,
                 start_latitude: float = None,
                 end_longitude: float = None,
                 end_latitude: float = None,
                 start_node=None,
                 end_node=None,
                 path_node_list=None,
                 is_idle_request: bool = False,
                 ):
        global ID
        self.ID = ID
        ID += 1

        if start_node and end_node:
            self.start_node = start_node
            self.end_node = end_node
        else:
            self.start_node = find_nearest_node(lat=start_latitude, lon=start_longitude, idx_dic=idx_dic,
                                                resolution=ENV["RESOLUTION"])
            self.end_node = find_nearest_node(lat=end_latitude, lon=end_longitude, idx_dic=idx_dic,
                                              resolution=ENV["RESOLUTION"])

        if start_longitude and start_longitude and end_longitude and end_latitude:
            self.start_longitude = start_longitude
            self.start_latitude = start_latitude
            self.end_longitude = end_longitude
            self.end_latitude = end_latitude
        else:
            self.start_latitude, self.start_longitude = graph_idx_2_coord[self.start_node]
            self.end_latitude, self.end_longitude = graph_idx_2_coord[self.end_node]

        if path_node_list:
            self.path_node_list = path_node_list
        else:
            if self.start_node == self.end_node:
                self.path_node_list = [self.start_node, self.end_node]
            else:
                try:
                    self.path_node_list = nx.shortest_path(G, self.start_node, self.end_node,
                                                           weight="length")  # 可能no path
                except:
                    print("卡到fine near node???")
                    start_node, start_lat, start_lon, end_node, end_lat, end_lon = find_nearest_node_except_specific_node(
                        start_lat=self.start_latitude, start_lon=self.start_longitude, start_node=self.start_node,
                        end_lat=self.end_latitude, end_lon=self.end_latitude, end_node=self.end_node,
                        idx_dic=idx_dic, resolution=ENV["RESOLUTION"]
                    )
                    print("没卡到 find near node")
                    self.start_latitude, self.start_longitude, self.start_node = start_lat, start_lon, start_node
                    self.end_latitude, self.end_longitude, self.end_node = end_lat, end_lon, end_node
                    self.path_node_list = nx.shortest_path(G, self.start_node, self.end_node,
                                                           weight="length")
                    print("找到路径")
        if self.start_node == self.end_node:
            self.path_distance_list = [0]
        else:
            route_gdf = ox.routing.route_to_gdf(G, self.path_node_list)
            self.path_distance_list = list(route_gdf['length'])

        self.request_total_distance = sum(self.path_distance_list)

        self.enable_share = enable_share
        self.is_pickup_request = is_pickup_request
        self.is_dropoff_request = is_dropoff_request
        self.is_idle_request = is_idle_request

        self.users = users
