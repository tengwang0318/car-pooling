import os

import h3
import tqdm
from env import *
from components.user import User
from components.vehicle import Vehicle
import pandas as pd
import random
from utils.vehicle_update_behaviour import *
from dispatch import *


def init_vehicle(number_of_vehicle, max_lat=ENV['max_lat'], min_lat=ENV['min_lat'], max_lon=ENV['max_lng'],
                 min_lon=ENV['min_lng']):
    for _ in range(number_of_vehicle):
        lat = random.uniform(min_lat, max_lat)
        lon = random.uniform(min_lon, max_lon)
        vehicle = Vehicle(latitude=lat, longitude=lon, velocity=ENV["velocity"])

        VEHICLES[vehicle.ID] = vehicle

        EMPTY_VEHICLES.add(vehicle)
        EMPTY_VEHICLES_IN_REGION[h3.geo_to_h3(lat=lat, lng=lon, resolution=ENV["RESOLUTION"])].add(vehicle)


def load_data(data_path=ENV['data_path']):
    df = pd.read_csv(data_path)
    stack = list()
    for order_start_time, order_lon, order_lat, dest_lon, dest_lat in \
            zip(df['order_start_time'].tolist()[::-1], df['order_lng'].tolist()[::-1], df['order_lat'].tolist()[::-1],
                df['dest_lng'].tolist()[::-1], df['dest_lat'].tolist()[::-1]):
        user = User(
            enable_share=True,
            # enable_share=random.random() > ENV['car_sharing_rate'],
            start_latitude=order_lat,
            start_longitude=order_lon,
            end_latitude=dest_lat,
            end_longitude=dest_lon,
            start_time=order_start_time,
        )
        stack.append((order_start_time, user))

        USERS[user]['start_time'] = order_start_time

    # return stack[-20:]
    return stack


def run_one_episode():
    stack = load_data()

    init_vehicle(ENV['vehicle_number'])
    current_users = []

    for idx, current_timestamp in enumerate(tqdm.tqdm(range(ENV['time'], 3600 * 16, ENV['time']))):
        if current_users:
            for user in current_users:
                USERS_IN_REGION[
                    h3.geo_to_h3(lat=user.start_latitude, lng=user.start_longitude, resolution=ENV["RESOLUTION"])].add(
                    user)

        while stack and stack[-1][0] < current_timestamp:
            user = stack.pop()[1]
            current_users.append(user)
            USERS_IN_REGION[
                h3.geo_to_h3(lat=user.start_latitude, lng=user.start_longitude, resolution=ENV["RESOLUTION"])].add(user)
        # print("准备开始分配订单")
        if current_users and (EMPTY_VEHICLES or IDLE_VEHICLES):
            # print("分配吗?")
            # random_dispatch(current_users, current_timestamp)
            current_users = mip_dispatch(current_users, current_timestamp)
        # print("订单分配完成，准备step")
        for vehicle in VEHICLES.values():
            vehicle.step()
        # print(f"当前time range{current_timestamp}, 车辆运动完成")
    for vehicle in VEHICLES.values():
        if vehicle.total_distance != 0:
            print(
                f"vehicle {vehicle.ID} total distance: {vehicle.total_distance}, pickup distance: {vehicle.pickup_distance}, and dropout distance: {vehicle.dropoff_distance}")


if __name__ == '__main__':
    run_one_episode()
    for user, val in USERS.items():
        if "pickup_time" in val:
            print(f"{user.user_id}: {val}, {user.user_id}'s cost: {user.cost}")
