from env import *
from .request import Request
from utils.cost import calculate_cost_for_finished_request, calculate_cost_for_unfinished_request

ID = 0


class Vehicle:
    def __init__(self,
                 latitude: float,
                 longitude: float,
                 current_capacity=0,
                 max_capacity=2,
                 status="EMPTY",
                 velocity=15
                 ):
        global ID
        self.ID = ID
        ID += 1

        self.time = 0

        self.status = status  # EMPTY, IDLE, FULL CAPACITY, PARTIALLY FULL
        self.latitude = latitude
        self.longitude = longitude
        self.current_capacity = current_capacity
        self.max_capacity = max_capacity

        self.current_requests = []
        self.has_sharing_request = False

        self.h3idx = h3.geo_to_h3(lat=latitude, lng=longitude, resolution=ENV['RESOLUTION'])
        self.velocity = velocity

        self.path_node_list1 = []
        self.pre_sum_dis1 = []

        self.path_node_list2 = []
        self.pre_sum_dis2 = []

        self.current_idx = 0  # 0 represents the middle position between node 1 and node 2
        self.current_distance = 0

        self.dropoff_distance = 0
        self.total_distance = 0
        self.pickup_distance = 0

        self.n1 = 0
        self.n2 = 0

    def update(self, requests: list[Request], has_requests=True):
        previous_region = self.h3idx

        current_distance_high_bound = 0
        previous_distance_high_bound = 0
        if has_requests:
            for request in self.current_requests:
                current_distance_high_bound += request.request_total_distance
                if self.current_distance < current_distance_high_bound:
                    calculate_cost_for_unfinished_request(self, request, self.current_distance,
                                                          previous_distance_high_bound)
                    break
                else:
                    calculate_cost_for_finished_request(self, request)
                    previous_distance_high_bound = current_distance_high_bound

        self.current_distance = 0

        self.current_requests = requests

        if requests:
            self.current_idx = 0
            one_request = True
            temp_path_node_list, temp_pre_sum_dis = [], [0]
            cnt_dropoff = 0
            for request in requests:
                temp_path_node_list = temp_path_node_list + request.path_node_list[
                                                            1:] if temp_path_node_list else request.path_node_list
                for temp_distance in request.path_distance_list:
                    temp_pre_sum_dis.append(temp_pre_sum_dis[-1] + temp_distance)
                if request.is_dropoff_request:
                    cnt_dropoff += 1

                    self.current_capacity += 1

                    if one_request:
                        self.path_node_list1 = temp_path_node_list
                        self.pre_sum_dis1 = temp_pre_sum_dis
                        one_request = False
                        temp_path_node_list, temp_pre_sum_dis = [], [0]
                    else:
                        self.path_node_list2 = temp_path_node_list
                        self.pre_sum_dis2 = temp_pre_sum_dis
            if cnt_dropoff == 0:
                self.pre_sum_dis1 = []
                self.pre_sum_dis2 = []
                self.path_node_list1 = []
                self.path_node_list2 = []
            elif cnt_dropoff == 1:
                self.pre_sum_dis2 = []
                self.path_node_list2 = []
            self.n1 = len(self.path_node_list1) if self.path_node_list1 else 0
            self.n2 = len(self.path_node_list2) if self.path_node_list2 else 0
        else:
            self.path_node_list1 = []
            self.pre_sum_dis1 = []
            self.n1 = 0

            self.path_node_list2 = []
            self.pre_sum_dis2 = []
            self.n2 = 0

            self.current_capacity = 0
        self.update_status(previous_region, is_idle=False)

    def update_when_idle(self, requests: [Request]):
        # reposition to a hot area so that it's enough for us to only use path 1
        previous_region = self.h3idx

        self.current_requests = requests
        self.current_capacity = 0
        self.current_distance = 0

        temp_path_node_list, temp_pre_sum_dis = [], [0]
        for request in requests:
            temp_path_node_list = temp_path_node_list + request.path_node_list[
                                                        1:] if temp_path_node_list else request.path_node_list
            for temp_distance in request.path_distance_list:
                temp_pre_sum_dis.append(temp_pre_sum_dis[-1] + temp_distance)
        self.path_node_list1 = temp_path_node_list
        self.pre_sum_dis1 = temp_pre_sum_dis
        self.path_node_list2 = []
        self.pre_sum_dis2 = []
        self.n1 = len(self.path_node_list1) if self.path_node_list1 else 0
        self.n2 = 0

        self.update_status(previous_region, is_idle=True)

    def update_status(self, previous_region, is_idle=False):
        previous_status = self.status
        if not is_idle:
            if self.current_capacity == self.max_capacity:
                self.status = "FULL CAPACITY"
                self.has_sharing_request = True
            elif self.current_capacity == self.max_capacity - 1:
                self.status = "PARTIALLY FULL"
                found = False
                for request in self.current_requests:
                    if request.is_dropoff_request and not request.enable_share:
                        found = True
                        break
                if found:
                    self.has_sharing_request = False
                else:
                    self.has_sharing_request = True
            else:
                self.status = "EMPTY"
                self.has_sharing_request = False
        else:
            self.status = "IDLE"
            self.has_sharing_request = False

        self.update_vehicle_dict(previous_status, previous_region)

    def update_vehicle_dict(self, previous_status, previous_region):
        if previous_status != self.status:
            if previous_status == "IDLE":
                IDLE_VEHICLES.discard(self)
            elif previous_status == "FULL CAPACITY":
                FULL_CAPACITY_VEHICLES.discard(self)
            elif previous_status == "PARTIALLY FULL":
                PARTIAL_CAPACITY_VEHICLES.discard(self)
            elif previous_status == "EMPTY":
                EMPTY_VEHICLES.discard(self)

            if self.status == "IDLE":
                IDLE_VEHICLES.add(self)
            elif self.status == "FULL CAPACITY":
                FULL_CAPACITY_VEHICLES.add(self)
            elif self.status == "PARTIALLY FULL":
                PARTIAL_CAPACITY_VEHICLES.add(self)
            elif self.status == "EMPTY":
                EMPTY_VEHICLES.add(self)

        if previous_status == "IDLE":
            IDLE_VEHICLES_IN_REGION[previous_region].discard(self)
        elif previous_status == "FULL CAPACITY":
            FULL_CAPACITY_VEHICLES_IN_REGION[previous_region].discard(self)
        elif previous_status == "PARTIALLY FULL":
            PARTIAL_CAPACITY_VEHICLES_IN_REGION[previous_region].discard(self)
        elif previous_status == "EMPTY":
            EMPTY_VEHICLES_IN_REGION[previous_region].discard(self)

        if self.status == "IDLE":
            IDLE_VEHICLES_IN_REGION[self.h3idx].add(self)
        elif self.status == "FULL CAPACITY":
            FULL_CAPACITY_VEHICLES_IN_REGION[self.h3idx].add(self)
        elif self.status == "PARTIALLY FULL":
            PARTIAL_CAPACITY_VEHICLES_IN_REGION[self.h3idx].add(self)
        elif self.status == "EMPTY":
            EMPTY_VEHICLES_IN_REGION[self.h3idx].add(self)

    def step(self):
        self.time += ENV['time']

        # 让他运行固定的时间，如果node list1 到终点了，那么就停下来，让他下车。
        if self.status != "IDLE" and self.status != "EMPTY":
            previous_region = self.h3idx
            if self.pre_sum_dis1 and self.path_node_list1:
                self.current_distance += self.velocity * ENV['time']
                # current_distance 与 pre_sum_dis1数量一样，一一对应

                while self.current_idx < self.n1 and self.current_distance < self.pre_sum_dis1[self.current_idx]:
                    self.current_idx += 1

                temp_idx = self.current_idx - 1
                self.latitude, self.longitude = graph_idx_2_coord[self.path_node_list1[temp_idx]]

                self.h3idx = h3.geo_to_h3(self.latitude, self.longitude, ENV['RESOLUTION'])

                if self.current_idx == self.n1 or self.current_distance >= self.pre_sum_dis1[-1]:  # 或者判断距离
                    self.current_distance = 0
                    self.current_idx = 0

                    temp_request = self.current_requests.pop(0)

                    while not temp_request.is_dropoff_request:
                        calculate_cost_for_finished_request(self, temp_request)
                        temp_request = self.current_requests.pop(0)

                    temp_user = temp_request.users[0]
                    USERS[temp_user]['end_time'] = self.time
                    calculate_cost_for_finished_request(self, temp_request)

                    print(f"vehicle {self.ID} 在 {self.time} s 跑完了一单 {self.longitude, self.latitude}")

                    self.current_capacity -= 1
                    self.update_status(previous_region)
                    if self.pre_sum_dis2 and self.path_node_list2:
                        self.pre_sum_dis1 = self.pre_sum_dis2
                        self.path_node_list1 = self.path_node_list2
                        self.n1 = self.n2
                        self.n2 = 0
                        self.pre_sum_dis2 = []
                        self.path_node_list2 = []
                    else:
                        self.pre_sum_dis1 = []
                        self.pre_sum_dis2 = []
                        self.path_node_list1 = []
                        self.path_node_list2 = []
                        self.n1 = 0
                        self.n2 = 0
                        # print("变成empty了吗？", self.status)
                else:
                    self.update_status(previous_region, is_idle=False)

        elif self.status == "IDLE":
            if self.current_idx == self.n1 or self.current_distance >= self.pre_sum_dis1[-1]:  # 停到原地不动了。
                idx = self.n1 - 1
                self.latitude, self.longitude = graph_idx_2_coord[self.path_node_list1[idx]]
                self.h3idx = h3.geo_to_h3(self.latitude, self.longitude, ENV['RESOLUTION'])
                self.total_distance += self.current_distance
                self.update([], has_requests=False)  # it will be empty.

            previous_region = self.h3idx
            self.current_distance += self.velocity * ENV['time']
            while self.current_idx < self.n1 and self.current_distance < self.pre_sum_dis1[self.current_idx]:
                self.current_idx += 1

            temp_idx = self.current_idx - 1
            self.latitude, self.longitude = graph_idx_2_coord[self.path_node_list1[temp_idx]]
            self.h3idx = h3.geo_to_h3(self.latitude, self.longitude, ENV['RESOLUTION'])
            self.update_vehicle_dict('IDLE', previous_region)


        elif self.status == "EMPTY":
            return
