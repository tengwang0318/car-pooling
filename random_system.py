from components.vehicle import Vehicle
from components.vehicle import Request
import random
from env import *
from components.user import User

num_vehicles = 15
users = [User() for i in range(20)]
vehicles = []
for _ in range(num_vehicles):
    lat, lon = random.choice(list(zip(nodes_lat, nodes_lon)))
    vehicle = Vehicle(latitude=lat, longitude=lon)
    vehicles.append(vehicle)

num_requests = 10
requests = []
for _ in range(num_requests):
    start_lat, start_lon = random.choice(list(zip(nodes_lat, nodes_lon)))
    end_lat, end_lon = random.choice(list(zip(nodes_lat, nodes_lon)))
    request = Request(
        start_longitude=start_lon,
        start_latitude=start_lat,
        end_longitude=end_lon,
        end_latitude=end_lat,
        enable_share=True,
        is_pickup_request=False,
        is_dropoff_request=True,
        users=[users[_]]
    )
    requests.append(request)
for _ in range(num_requests):
    start_lat, start_lon = random.choice(list(zip(nodes_lat, nodes_lon)))
    end_lat, end_lon = random.choice(list(zip(nodes_lat, nodes_lon)))
    request = Request(
        start_longitude=start_lon,
        start_latitude=start_lat,
        end_longitude=end_lon,
        end_latitude=end_lat,
        enable_share=False,
        is_pickup_request=False,
        is_dropoff_request=True,
        users=[users[_]]
    )
    requests.append(request)

for i in range(10):
    start_lat, start_lon = vehicles[i].latitude, vehicles[i].longitude
    end_lat, end_lon = requests[i].start_latitude, requests[i].start_longitude
    temp_request = Request(
        start_longitude=start_lon,
        start_latitude=start_lat,
        end_longitude=end_lon,
        end_latitude=end_lat,
        enable_share=False,
        is_pickup_request=True,
        is_dropoff_request=False,
        users=[]

    )
    vehicles[i].update([temp_request, requests[i]])

for i in range(5):
    start_lat, start_lon = vehicles[i].latitude, vehicles[i].longitude
    v1_lat, v1_lon = requests[10 + 2 * i].start_latitude, requests[10 + 2 * i].start_longitude
    v2_lat, v2_lon = requests[10 + 2 * i + 1].start_latitude, requests[10 + 2 * i + 1].start_longitude
    v1_lat_end, v1_lon_end = requests[10 + 2 * i].end_latitude, requests[10 + 2 * i].end_longitude
    v2_lat_end, v2_lon_end = requests[10 + 2 * i + 1].end_latitude, requests[10 + 2 * i + 1].end_longitude
    request1 = Request(
        start_longitude=start_lon,
        start_latitude=start_lat,
        end_longitude=v1_lon,
        end_latitude=v1_lat,
        enable_share=True,
        is_pickup_request=True,
        is_dropoff_request=False,
        users=[]
    )
    request2 = Request(
        start_longitude=v1_lon,
        start_latitude=v1_lat,
        end_longitude=v2_lon,
        end_latitude=v2_lat,
        enable_share=True,
        is_pickup_request=True,
        is_dropoff_request=False,
        users=[users[10 + 2 * i]],

    )
    request3 = Request(
        start_longitude=v2_lon,
        start_latitude=v2_lat,
        end_longitude=v1_lon_end,
        end_latitude=v1_lat_end,
        enable_share=True,
        is_pickup_request=False,
        is_dropoff_request=True,
        users=[users[10 + 2 * i], users[10 + 2 * i + 1]]
    )
    request4 = Request(
        start_longitude=v1_lon_end,
        start_latitude=v1_lat_end,
        end_longitude=v2_lon_end,
        end_latitude=v2_lat_end,
        enable_share=True,
        is_pickup_request=False,
        is_dropoff_request=True,
        users=[users[11 + 2 * i]]

    )
    vehicles[10 + i].update([request1, request2, request3, request4])
#
# for i in range(3):
#     start_lat, start_lon = vehicles[i].latitude, vehicles[i].longitude
#     v1_lat, v1_lon = requests[14 + 2 * i].start_latitude, requests[14 + 2 * i].start_longitude
#     v2_lat, v2_lon = requests[14 + 2 * i + 1].start_latitude, requests[14 + 2 * i + 1].start_longitude
#     v1_lat_end, v1_lon_end = requests[14 + 2 * i].end_latitude, requests[14 + 2 * i].end_longitude
#     v2_lat_end, v2_lon_end = requests[14 + 2 * i + 1].end_latitude, requests[14 + 2 * i + 1].end_longitude
#
#     request1 = Request(
#         start_longitude=start_lon,
#         start_latitude=start_lat,
#         end_longitude=v1_lon,
#         end_latitude=v1_lat,
#         enable_share=True,
#         is_pickup_request=True,
#         is_dropoff_request=False
#     )
#     request2 = Request(
#         start_longitude=v1_lon,
#         start_latitude=v1_lat,
#         end_longitude=v2_lon,
#         end_latitude=v2_lat,
#         enable_share=True,
#         is_pickup_request=True,
#         is_dropoff_request=False
#     )
#     request3 = Request(
#         start_longitude=v2_lon,
#         start_latitude=v2_lat,
#         end_longitude=v1_lon_end,
#         end_latitude=v1_lat_end,
#         enable_share=True,
#         is_pickup_request=False,
#         is_dropoff_request=True,
#     )
#     request4 = Request(
#         start_longitude=v1_lon_end,
#         start_latitude=v1_lat_end,
#         end_longitude=v2_lon_end,
#         end_latitude=v2_lat_end,
#         enable_share=True,
#         is_pickup_request=False,
#         is_dropoff_request=True
#
#     )
# for vehicle in vehicles:
#     print(f"the number of request in vehicle {vehicle.ID} is {len(vehicle.current_requests)}")

for step in range(10000):  # 假设运行100步

    for vehicle in vehicles:
        vehicle.step()

    # 打印每一步的仿真状态
    # for i, vehicle in enumerate(vehicles):
    #     print(
    #         f"Vehicle {i}: Latitude = {vehicle.latitude}, Longitude = {vehicle.longitude}, Status = {vehicle.status}, Capacity = {vehicle.current_capacity}")

    # 请根据需要调整变量和参数
print("-----\n\n")
for vehicle in vehicles:
    print(f"Vehicle {vehicle.ID}'s total distance is {vehicle.total_distance}")
print("-----\n\n")
for user in users:
    print(f"User {user.user_id}'s cost is {user.cost}")
