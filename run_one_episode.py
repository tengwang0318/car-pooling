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

        USERS[user.user_id]['start_time'] = order_start_time

    return stack


def run_one_episode():
    stack = load_data()
    init_vehicle(1000)
    for current_timestamp in tqdm.tqdm(range(ENV['time'], 3600 * 16, ENV['time'])):

        current_users = []
        while stack and stack[-1][0] < current_timestamp:
            user = stack.pop()[1]
            current_users.append(user)
            # USERS_IN_REGION[
            #     h3.geo_to_h3(lat=user.start_latitude, lng=user.start_longitude, resolution=ENV["RESOLUTION"])].add(user)
        # random_dispatch(current_users, current_timestamp)
        mip_dispatch(current_users, current_timestamp)
        for vehicle in VEHICLES.values():
            vehicle.step()
    for vehicle in VEHICLES.values():
        if vehicle.total_distance != 0:
            print(
                f"vehicle total distance: {vehicle.total_distance}, pickup distance: {vehicle.pickup_distance}, and dropout distance: {vehicle.dropoff_distance}")


if __name__ == '__main__':
    run_one_episode()
    for user, val in USERS.items():
        if user.cost != 0:
            print(f"{user.user_id}: {val}, {user.user_id}'s cost: {user.cost}")
