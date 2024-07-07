from components.request import Request
from components.vehicle import Vehicle
from components.user import User
from env import *
from utils.find_nearest_node import find_nearest_node

"""
update the status of vehicle, including status, requests, position
"""


def vehicle_update_for_one_user(vehicle: Vehicle,
                                user: User):
    """
    仅考虑一个request
    """
    vehicle_start_longitude, vehicle_start_latitude = vehicle.longitude, vehicle.latitude
    vehicle_node = find_nearest_node(vehicle_start_latitude, vehicle_start_longitude, idx_dic, ENV['resolution'])
    vehicle_start_latitude, vehicle_start_longitude = graph_idx_2_coord[vehicle_node]

    req_start_lat, req_start_lon = user.start_latitude, user.start_longitude
    req_end_lat, req_end_lon = user.end_latitude, user.end_longitude

    requests = []
    request_start_nearest_node = find_nearest_node(req_start_lat, req_start_lon, idx_dic, ENV['resolution'])
    req_start_lat, req_start_lon = graph_idx_2_coord[request_start_nearest_node]
    request_end_nearest_node = find_nearest_node(req_end_lat, req_end_lon, idx_dic, ENV["resolution"])
    req_end_lat, req_end_lon = graph_idx_2_coord[request_end_nearest_node]

    request1 = Request(
        start_longitude=vehicle_start_longitude,
        start_latitude=vehicle_start_latitude,
        end_longitude=req_start_lon,
        end_latitude=req_start_lat,
        enable_share=False,  # 接客不管
        is_pickup_request=True,
        is_dropoff_request=False,
        users=[],
        start_node=vehicle_node,
        end_node=request_start_nearest_node,
        path_node_list=None  # 以后可以改
    )
    requests.append(request1)

    request2 = Request(
        start_longitude=req_start_lon,
        start_latitude=req_start_lat,
        end_longitude=req_end_lon,
        end_latitude=req_end_lat,
        enable_share=user.enable_share,
        is_pickup_request=False,
        is_dropoff_request=True,
        users=[user],
        start_node=request_start_nearest_node,
        end_node=request_end_nearest_node,
        path_node_list=None  # 以后可以改
    )
    requests.append(request2)
    vehicle.has_sharing_request = bool(sum([request.enable_share for request in requests]))
    vehicle.update(requests)


def vehicle_update_for_two_users_at_same_time(vehicle: Vehicle,
                                              user1: User,
                                              user2: User,
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
        enable_share=False,
        is_pickup_request=True,
        is_dropoff_request=False,
        users=[],
        start_node=vehicle_nearest_node,
        end_node=req1_start_nearest_node,
        path_node_list=None  # 未知，to do list
    )
    requests.append(request1)

    request2 = Request(
        start_longitude=req1_start_lon,
        start_latitude=req1_start_lat,
        end_longitude=req2_start_lon,
        end_latitude=req2_end_lat,
        enable_share=False,
        is_pickup_request=True,
        is_dropoff_request=False,
        users=[user1],
        start_node=req1_start_nearest_node,
        end_node=req2_start_nearest_node,
        path_node_list=None
    )
    requests.append(request2)

    req3 = Request(
        start_longitude=req2_start_lon,
        start_latitude=req2_start_lat,
        end_longitude=req1_end_lon,
        end_latitude=req1_end_lat,
        enable_share=user1.enable_share,  # 应该是True，之后再check，
        is_pickup_request=False,
        is_dropoff_request=True,
        users=[user1, user2],
        start_node=req2_start_nearest_node,
        end_node=req1_end_nearest_node,
        path_node_list=None
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
        users=[user2],
        start_node=req1_end_nearest_node,
        end_node=req2_end_nearest_node,
        path_node_list=None
    )
    requests.append(req4)

    vehicle.has_sharing_request = bool(sum([request.enable_share for request in requests]))
    vehicle.update(requests)


def vehicle_update_for_two_users_after_u1_heading(vehicle: Vehicle,
                                                  user1: User,
                                                  user2: User):
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
        enable_share=False,
        is_pickup_request=True,
        is_dropoff_request=False,
        users=[user1],
        start_node=vehicle_nearest_node,
        end_node=req2_start_nearest_node,
        path_node_list=None
    )
    requests.append(request1)

    request2 = Request(
        start_longitude=req2_start_lon,
        start_latitude=req2_start_lat,
        end_longitude=req1_end_lon,
        end_latitude=req1_end_lat,
        enable_share=user2.enable_share,
        is_pickup_request=False,
        is_dropoff_request=True,
        users=[user2, user1],
        start_node=req2_start_nearest_node,
        end_node=req1_end_nearest_node,
        path_node_list=None
    )
    requests.append(request2)

    request3 = Request(
        start_longitude=req1_end_lon,
        start_latitude=req1_end_lat,
        end_longitude=req2_end_lon,
        end_latitude=req2_end_lat,
        enable_share=user1.enable_share,
        is_pickup_request=False,
        is_dropoff_request=True, users=[user2],
        start_node=req1_end_nearest_node,
        end_node=req2_end_nearest_node,
        path_node_list=None
    )
    requests.append(request3)

    vehicle.has_sharing_request = bool(sum([request.enable_share for request in requests]))
    vehicle.update(requests)
