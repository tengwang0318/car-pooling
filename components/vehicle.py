import h3
from env import ENV, G
from request import Request


class Vehicle:
    def __init__(self,
                 latitude: float,
                 longitude: float,

                 request1: Request,
                 request2: Request,

                 current_capacity=0,
                 max_capacity=2,
                 status="EMPTY",
                 velocity=15,

                 path_node_list1=[],
                 pre_sum_dis1=[],

                 path_node_list2=[],
                 pre_sum_dis2=[],

                 current_idx=0,
                 current_distance=0,
                 current_requests=[]
                 ):

        self.status = status  # EMPTY, IDLE, FULL CAPACITY, PARTIALLY FULL
        self.latitude = latitude
        self.longitude = longitude
        self.current_capacity = current_capacity
        self.max_capacity = max_capacity

        self.current_requests = current_requests  # it consists at most two requests.
        self.has_sharing_request = False

        self.h3idx = h3.geo_to_h3(lat=latitude, lng=longitude, resolution=ENV['resolution'])  # 这个有没有必要呢?
        self.velocity = velocity

        self.path_node_list1 = path_node_list1
        self.pre_sum_dis1 = pre_sum_dis1
        self.current_idx = current_idx  # 0 represents the middle position between node 1 and node 2

        self.path_node_list2 = path_node_list2
        self.pre_sum_dis2 = pre_sum_dis2

        self.current_distance = current_distance
        self.n1 = len(self.path_node_list1)
        self.n2 = len(self.path_node_list2)

        # self.G = G

    def update_path(self, request1: Request, request2: Request):
        # if node list1 is None, then node list2 must be None too.
        # if node list1 is not None, node list2 is None
        # if both node list1 and node list2 are not None,
        path_node_list1 = request1.path_node_list if request1 else None
        path_distance_list1 = request1.path_distance_list if request1 else None

        path_node_list2 = request2.path_node_list if request2 else None
        path_distance_list2 = request2.path_distance_list if request2 else None

        self.current_distance = 0
        if path_distance_list1 and path_node_list1:
            self.path_node_list1 = path_node_list1
            self.n1 = len(self.path_node_list1)
            self.pre_sum_dis1 = [0] * (self.n1 + 1)
            for i in range(1, self.n1 + 1):
                self.pre_sum_dis1[i] = self.pre_sum_dis1[i - 1] + path_distance_list1[i - 1]
            self.current_idx = 0

            if path_distance_list2 and path_node_list2:
                self.path_node_list2 = path_node_list2
                self.n2 = len(self.path_node_list2)
                self.pre_sum_dis2 = [0] * (1 + self.n2)
                for i in range(1, self.n2 + 1):
                    self.pre_sum_dis2[i] = self.pre_sum_dis2[i - 1] + path_distance_list2[i - 1]
                self.current_requests = [request1, request2]
            else:
                self.path_node_list2 = []
                self.n2 = 0
                self.pre_sum_dis2 = []
                self.current_requests = [request1]
        else:
            self.path_node_list1 = []
            self.path_node_list2 = []
            self.pre_sum_dis1 = []
            self.pre_sum_dis2 = []
            self.n1 = 0
            self.n2 = 0
            self.current_requests = []

    def update_status(self):
        if not self.current_requests:
            self.status = "EMPTY"
            self.has_sharing_request = True
        elif len(self.current_requests) == 1:
            current_request = self.current_requests[0]
            if current_request.allow_sharing:
                self.has_sharing_request = True

            else:
                self.has_sharing_request = False
            self.status = "PARTIALLY FULL"
        else:
            self.has_sharing_request = True
            self.status = "FULL CAPACITY"

    def step(self):
        # 让他运行固定的时间，如果node list1 到终点了，那么就停下来，让他下车。
        if self.pre_sum_dis1 and self.path_node_list1:
            self.current_distance += self.velocity * self.env['time']
            while self.current_idx < self.n1 and self.current_distance < self.pre_sum_dis1[self.current_idx + 1]:
                self.current_idx += 1

            temp_idx = self.current_idx if self.current_idx < self.n1 else self.current_idx - 1
            node = self.G[self.path_node_list1[temp_idx]]
            self.latitude = node['x']
            self.longitude = node['y']
            self.h3idx = h3.geo_to_h3(self.latitude, self.latitude, self.env['resolution'])

            if self.current_idx == self.n1 or self.current_distance >= self.pre_sum_dis1[-1]:  # 或者判断距离
                self.current_distance = 0
                self.current_idx = 0
                self.current_requests.pop(0)
                self.update_status()
                if self.pre_sum_dis2 and self.path_node_list2:
                    self.pre_sum_dis1 = self.pre_sum_dis2
                    self.path_node_list1 = self.path_node_list2
                    self.n1 = self.n2
                    self.n2 = 0
                    self.pre_sum_dis2 = []
                    self.path_node_list2 = []
                else:
                    self.pre_sum_dis1 = []
                    self.path_node_list1 = []
                    self.n1 = 0
            # else:
            #     self.current_idx -= 1

        else:
            pass
