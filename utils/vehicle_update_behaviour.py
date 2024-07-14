from components.request import Request
from components.vehicle import Vehicle
from components.user import User
from env import *
from utils.find_nearest_node import find_nearest_node

"""
update the status of vehicle, including status, requests, position
"""


def vehicle_update_for_one_user(vehicle: Vehicle,
                                user: User,
                                path_node_lists=(None, None),
                                time=None):
    """
    仅考虑一个request
    """
    if path_node_lists is None:
        path_node_lists = [None, None]
    vehicle_start_longitude, vehicle_start_latitude = vehicle.longitude, vehicle.latitude
    vehicle_node = find_nearest_node(vehicle_start_latitude, vehicle_start_longitude, idx_dic, ENV['RESOLUTION'])
    vehicle_start_latitude, vehicle_start_longitude = graph_idx_2_coord[vehicle_node]

    req_start_lat, req_start_lon = user.start_latitude, user.start_longitude
    req_end_lat, req_end_lon = user.end_latitude, user.end_longitude

    requests = []
    request_start_nearest_node = find_nearest_node(req_start_lat, req_start_lon, idx_dic, ENV['RESOLUTION'])
    req_start_lat, req_start_lon = graph_idx_2_coord[request_start_nearest_node]
    request_end_nearest_node = find_nearest_node(req_end_lat, req_end_lon, idx_dic, ENV["RESOLUTION"])
    req_end_lat, req_end_lon = graph_idx_2_coord[request_end_nearest_node]

    request1 = Request(
        start_longitude=vehicle_start_longitude,
        start_latitude=vehicle_start_latitude,
        end_longitude=req_start_lon,
        end_latitude=req_start_lat,
        enable_share=True,  # 接客默认为true, 实际判断的时候看的是enable share && is dropoff request
        is_pickup_request=True,
        is_dropoff_request=False,
        is_idle_request=False,
        users=[],
        start_node=vehicle_node,
        end_node=request_start_nearest_node,
        path_node_list=path_node_lists[0],  # it may be updated later, the default value of it is None.
    )

    USERS[user.user_id]['pickup_time'] = request1.request_total_distance / vehicle.velocity + time
    requests.append(request1)

    request2 = Request(
        start_longitude=req_start_lon,
        start_latitude=req_start_lat,
        end_longitude=req_end_lon,
        end_latitude=req_end_lat,
        enable_share=user.enable_share,
        is_pickup_request=False,
        is_dropoff_request=True,
        is_idle_request=False,
        users=[user],
        start_node=request_start_nearest_node,
        end_node=request_end_nearest_node,
        path_node_list=path_node_lists[1]  # it may be updated later, the default value of it is None.
    )
    requests.append(request2)

    vehicle.update(requests)


def vehicle_update_for_two_users_at_same_time(vehicle: Vehicle,
                                              user1: User,
                                              user2: User,
                                              path_node_lists: (None, None, None, None),
                                              time=None,
                                              ):
    """
    默认user1更近，这里可以判断，但是没必要，我盲猜OR部分已经判断过了
    """
    req1_start_lat = user1.start_latitude
    req1_start_lon = user1.start_longitude
    req1_end_lat = user1.end_latitude
    req1_end_lon = user1.end_longitude
    req2_start_lat = user2.start_latitude
    req2_start_lon = user2.start_longitude
    req2_end_lat = user2.end_latitude
    req2_end_lon = user2.end_longitude

    vehicle_lat, vehicle_lon = vehicle.latitude, vehicle.longitude

    req1_start_nearest_node = find_nearest_node(req1_start_lat, req1_start_lon, idx_dic, ENV['resolution'])
    req1_end_nearest_node = find_nearest_node(req1_end_lat, req1_end_lon, idx_dic, ENV['resolution'])
    req2_start_nearest_node = find_nearest_node(req2_start_lat, req2_start_lon, idx_dic, ENV['resolution'])
    req2_end_nearest_node = find_nearest_node(req2_end_lat, req2_end_lon, idx_dic, ENV['resolution'])
    vehicle_nearest_node = find_nearest_node(vehicle_lat, vehicle_lon, idx_dic, ENV['resolution'])

    req1_start_lat, req1_start_lon = graph_idx_2_coord[req1_start_nearest_node]
    req2_start_lat, req2_start_lon = graph_idx_2_coord[req2_start_nearest_node]
    req1_end_lat, req1_end_lon = graph_idx_2_coord[req1_end_nearest_node]
    req2_end_lat, req2_end_lon = graph_idx_2_coord[req2_end_nearest_node]
    vehicle_lat, vehicle_lon = graph_idx_2_coord[vehicle_nearest_node]

    requests = []

    request1 = Request(
        start_longitude=vehicle_lon,
        start_latitude=vehicle_lat,
        end_longitude=req1_start_lon,
        end_latitude=req1_start_lat,
        enable_share=True,
        is_pickup_request=True,
        is_dropoff_request=False,
        is_idle_request=False,
        users=[],
        start_node=vehicle_nearest_node,
        end_node=req1_start_nearest_node,
        path_node_list=path_node_lists[0]
    )
    USERS[user1.user_id]['pickup_time'] = time + request1.request_total_distance / vehicle.velocity
    requests.append(request1)

    request2 = Request(
        start_longitude=req1_start_lon,
        start_latitude=req1_start_lat,
        end_longitude=req2_start_lon,
        end_latitude=req2_end_lat,
        enable_share=True,
        is_pickup_request=True,
        is_dropoff_request=False,
        is_idle_request=False,
        users=[user1],
        start_node=req1_start_nearest_node,
        end_node=req2_start_nearest_node,
        path_node_list=path_node_lists[1],
    )
    USERS[user2.user_id]['pickup_time'] = time + (
            request1.request_total_distance + request2.request_total_distance) / vehicle.velocity
    requests.append(request2)

    req3 = Request(
        start_longitude=req2_start_lon,
        start_latitude=req2_start_lat,
        end_longitude=req1_end_lon,
        end_latitude=req1_end_lat,
        enable_share=user1.enable_share,  # 应该是True，之后再check. 应该事先就确认过了
        is_pickup_request=False,
        is_dropoff_request=True,
        is_idle_request=False,
        users=[user1, user2],
        start_node=req2_start_nearest_node,
        end_node=req1_end_nearest_node,
        path_node_list=path_node_lists[2]
    )
    requests.append(req3)

    req4 = Request(
        start_longitude=req1_end_lon,
        start_latitude=req1_end_lat,
        end_latitude=req2_end_lat,
        end_longitude=req2_end_lon,
        enable_share=user2.enable_share,
        is_pickup_request=False,
        is_dropoff_request=True,
        is_idle_request=False,
        users=[user2],
        start_node=req1_end_nearest_node,
        end_node=req2_end_nearest_node,
        path_node_list=path_node_lists[3]
    )
    requests.append(req4)

    vehicle.update(requests)


def vehicle_update_for_two_users_after_u1_heading(vehicle: Vehicle,
                                                  user1: User,
                                                  user2: User,
                                                  path_node_lists: (None, None, None),
                                                  time=None):
    req1_end_lat = user1.end_latitude
    req1_end_lon = user1.end_longitude
    req2_start_lat = user2.start_latitude
    req2_start_lon = user2.start_longitude
    req2_end_lat = user2.end_latitude
    req2_end_lon = user2.end_longitude

    vehicle_lat, vehicle_lon = vehicle.latitude, vehicle.longitude
    req1_end_nearest_node = find_nearest_node(req1_end_lat, req1_end_lon, idx_dic, ENV['resolution'])
    req2_start_nearest_node = find_nearest_node(req2_start_lat, req2_start_lon, idx_dic, ENV['resolution'])
    req2_end_nearest_node = find_nearest_node(req2_end_lat, req2_end_lon, idx_dic, ENV['resolution'])
    vehicle_nearest_node = find_nearest_node(vehicle_lat, vehicle_lon, idx_dic, ENV['resolution'])

    req2_start_lat, req2_start_lon = graph_idx_2_coord[req2_start_nearest_node]
    req1_end_lat, req1_end_lon = graph_idx_2_coord[req1_end_nearest_node]
    req2_end_lat, req2_end_lon = graph_idx_2_coord[req2_end_nearest_node]
    vehicle_lat, vehicle_lon = graph_idx_2_coord[vehicle_nearest_node]

    requests = []

    request1 = Request(
        start_longitude=vehicle_lon,
        start_latitude=vehicle_lat,
        end_longitude=req2_start_lon,
        end_latitude=req2_start_lat,
        enable_share=True,
        is_pickup_request=True,
        is_idle_request=False,
        is_dropoff_request=False,
        users=[user1],
        start_node=vehicle_nearest_node,
        end_node=req2_start_nearest_node,
        path_node_list=path_node_lists[0],

    )
    USERS[user2.user_id]['pickup_time'] = time + request1.request_total_distance / vehicle.velocity

    requests.append(request1)

    request2 = Request(
        start_longitude=req2_start_lon,
        start_latitude=req2_start_lat,
        end_longitude=req1_end_lon,
        end_latitude=req1_end_lat,
        enable_share=user2.enable_share and user1.enable_share,
        is_pickup_request=False,
        is_dropoff_request=True,
        is_idle_request=False,
        users=[ user1,user2],
        start_node=req2_start_nearest_node,
        end_node=req1_end_nearest_node,
        path_node_list=path_node_lists[1]
    )
    requests.append(request2)

    request3 = Request(
        start_longitude=req1_end_lon,
        start_latitude=req1_end_lat,
        end_longitude=req2_end_lon,
        end_latitude=req2_end_lat,
        enable_share=user2.enable_share,
        is_pickup_request=False,
        is_dropoff_request=True,
        is_idle_request=False,
        users=[user2],
        start_node=req1_end_nearest_node,
        end_node=req2_end_nearest_node,
        path_node_list=path_node_lists[2]
    )
    requests.append(request3)

    vehicle.update(requests)


def vehicle_update_for_repositioning(vehicle: Vehicle,
                                     latitude: float,
                                     longitude: float,
                                     path_node_lists=(None)):
    vehicle_start_longitude, vehicle_start_latitude = vehicle.longitude, vehicle.latitude
    vehicle_node = find_nearest_node(vehicle_start_latitude, vehicle_start_longitude, idx_dic, ENV["RESOLUTION"])
    vehicle_start_latitude, vehicle_start_longitude = graph_idx_2_coord[vehicle_node]

    reposition_latitude, reposition_longitude = latitude, longitude
    reposition_node = find_nearest_node(reposition_latitude, reposition_longitude, idx_dic, ENV['RESOLUTION'])
    request = Request(
        start_latitude=vehicle_start_latitude,
        start_longitude=vehicle_start_longitude,
        end_longitude=reposition_longitude,
        end_latitude=reposition_latitude,
        start_node=vehicle_node,
        end_node=reposition_node,
        path_node_list=path_node_lists[0],
        enable_share=True,
        is_pickup_request=False,
        is_dropoff_request=False,
        is_idle_request=True,
        users=[]
    )
    requests = [request]
    vehicle.update_when_idle(requests)
