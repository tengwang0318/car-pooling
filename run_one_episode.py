import sys

import tqdm

from env import *
from components.user import User
from components.vehicle import Vehicle
import pandas as pd
import random
from utils.vehicle_update_behaviour import *
from dispatch import *
import multiprocessing


def init_vehicle(number_of_vehicle, max_lat=ENV['max_lat'], min_lat=ENV['min_lat'], max_lon=ENV['max_lng'],
                 min_lon=ENV['min_lng']):
    vehicles = []
    for _ in range(number_of_vehicle):
        lat = random.uniform(min_lat, max_lat)
        lon = random.uniform(min_lon, max_lon)
        vehicle = Vehicle(latitude=lat, longitude=lon)
        VEHICLES[vehicle.ID] = vehicle
        vehicles.append(vehicle)
        EMPTY_VEHICLES.add(vehicle)
    return vehicles


def load_data(data_path=ENV['data_path']):
    df = pd.read_csv(data_path)
    stack = list()
    for order_start_time, order_lon, order_lat, dest_lon, dest_lat in \
            zip(df['order_start_time'].tolist()[::-1], df['order_lng'].tolist()[::-1], df['order_lat'].tolist()[::-1],
                df['dest_lng'].tolist()[::-1], df['dest_lat'].tolist()[::-1]):
        user = User(enable_share=random.random() > ENV['car_sharing_rate'],
                    start_latitude=order_lat,
                    start_longitude=order_lon,
                    end_latitude=dest_lat,
                    end_longitude=dest_lon
                    )
        stack.append((order_start_time, user))
        USERS[user.user_id] = user
    return stack


def vehicle_step(vehicle: Vehicle):
    sys.stdout.flush()
    vehicle.step()
def run_one_episode():
    stack = load_data()
    vehicles = init_vehicle(100)
    for current_timestamp in tqdm.tqdm(range(ENV['time'], 3600 * 16, ENV['time'])):

        current_users = []
        while stack and stack[-1][0] < current_timestamp:
            user = stack.pop()[1]
            current_users.append(user)
        random_dispatch(current_users)

        for vehicle in vehicles:
            vehicle.step()


        # with multiprocessing.Pool(processes=4) as pool:
        #     pool.map(vehicle_step, vehicles)


if __name__ == '__main__':
    run_one_episode()
