import heapq
import os
import random
from utils.vehicle_update_behaviour import *
from utils.heuristic_partition import heuristic_partition
from utils.build_MIP_model import build_and_solve_model
from utils.parser import parser
from data_preprocessing.map_preprocessing.preprocess import find_nearby_hexagons
from utils.vehicle_update_behaviour import *


def random_dispatch(current_users: list[User], current_time):
    if current_users:
        print(f"current users are as follows: {[user.user_id for user in current_users]}")
    while current_users:
        temp_user = current_users.pop()
        temp_vehicle = random.choice(list(EMPTY_VEHICLES) + list(IDLE_VEHICLES))
        try:
            vehicle_update_for_one_user(vehicle=temp_vehicle,
                                        user=temp_user,
                                        time=current_time)
            print(f"Vehicle {temp_vehicle.ID} 去接 {temp_user.user_id}")

        except Exception as e:

            print(e)
            print(f"current user is {temp_user}")
            current_users.append(temp_user)

            continue


def classify_the_number_order_and_vehicle(current_users: list[User]):
    regions = heuristic_partition(current_users)
    more_vehicles, more_orders = [], []
    for region in regions:
        vehicles_cnt = 0
        # test_vehicle_cnt = 0
        order_cnt = region[-1]
        for sub_area in region[:-1]:
            vehicles_cnt += len(EMPTY_VEHICLES_IN_REGION[sub_area])
            vehicles_cnt += len(IDLE_VEHICLES_IN_REGION[sub_area])

            # test_vehicle_cnt += len(set(EMPTY_VEHICLES_IN_REGION[sub_area]))
            # test_vehicle_cnt += len(set(IDLE_VEHICLES_IN_REGION[sub_area]))
            # assert test_vehicle_cnt == vehicles_cnt
            # vehicles_cnt += PARTIAL_CAPACITY_VEHICLES_IN_REGION[sub_area]
        if vehicles_cnt >= order_cnt:
            more_vehicles.append(region)
        else:
            more_orders.append((order_cnt - vehicles_cnt, region))
    heapq.heapify(more_orders)

    return more_vehicles, more_orders


def parse_mip_and_dispatch(model, empty_vehicles, partial_capacity_vehicles, users, current_time):
    x_s, y_s, z_s = parser(model)
    for vehicle_idx, user_idx in x_s:
        temp_vehicle = empty_vehicles[vehicle_idx]
        temp_user = users[user_idx]
        vehicle_update_for_one_user(temp_vehicle, temp_user, time=current_time)

    for vehicle_idx, user1_idx, user2_idx in y_s:
        temp_vehicle = empty_vehicles[vehicle_idx]
        temp_user1 = users[user1_idx]
        temp_user2 = users[user2_idx]

        vehicle_update_for_two_users_at_same_time(temp_vehicle, temp_user1, temp_user2, time=current_time)
    for vehicle_idx, user_idx in z_s:
        temp_vehicle = partial_capacity_vehicles[vehicle_idx]
        try:
            temp_user1 = temp_vehicle.current_requests[1].users[0]
        except:
            temp_user1 = temp_vehicle.current_requests[0].users[0]
        temp_user2 = users[user_idx]
        vehicle_update_for_two_users_after_u1_heading(temp_vehicle, temp_user1, temp_user2, time=current_time)


def mip_dispatch(current_users: list[User], current_time):
    more_vehicles, more_orders = classify_the_number_order_and_vehicle(current_users)

    for more_vehicle_region in more_vehicles:
        empty_vehicles, partial_capacity_vehicles = [], []
        users = []
        for more_vehicle_subarea in more_vehicle_region[:-1]:
            empty_vehicles.extend(list(EMPTY_VEHICLES_IN_REGION[more_vehicle_subarea]))
            empty_vehicles.extend(list(IDLE_VEHICLES_IN_REGION[more_vehicle_subarea]))
            partial_capacity_vehicles.extend(list(PARTIAL_CAPACITY_VEHICLES_IN_REGION[more_vehicle_subarea]))
            users.extend(USERS_IN_REGION[more_vehicle_subarea])
        assert len(empty_vehicles) == len(set(empty_vehicles))

        model = build_and_solve_model(empty_vehicles, partial_capacity_vehicles, users)

        parse_mip_and_dispatch(model, empty_vehicles, partial_capacity_vehicles, users, current_time)

    failures = []
    for gap, more_orders_region in more_orders:
        visited_subareas = set()

        empty_vehicles, partial_capacity_vehicles = [], []
        users = []
        for more_vehicle_subarea in more_orders_region[:-1]:
            if more_vehicle_subarea in visited_subareas:
                continue
            empty_vehicles.extend(EMPTY_VEHICLES_IN_REGION[more_vehicle_subarea])
            empty_vehicles.extend(IDLE_VEHICLES_IN_REGION[more_vehicle_subarea])
            partial_capacity_vehicles.extend(PARTIAL_CAPACITY_VEHICLES_IN_REGION[more_vehicle_subarea])
            users.extend(USERS_IN_REGION[more_vehicle_subarea])

            visited_subareas.add(more_vehicle_subarea)
            assert len(users) == len(set(users))
            assert len(empty_vehicles) == len(set(empty_vehicles))

            if gap > 0:
                k = 1
                while k <= 5:
                    seen_subarea = [more_vehicle_subarea]
                    for near_idx in find_nearby_hexagons(more_vehicle_subarea, k):
                        if near_idx in visited_subareas:
                            continue

                        if len(EMPTY_VEHICLES_IN_REGION[near_idx]) != 0 or len(
                                IDLE_VEHICLES_IN_REGION[near_idx]) != 0:
                            visited_subareas.add(near_idx)
                            gap -= (len(EMPTY_VEHICLES_IN_REGION[near_idx]) + len(
                                IDLE_VEHICLES_IN_REGION[near_idx]))
                            if len(EMPTY_VEHICLES_IN_REGION[near_idx]) != 0:
                                empty_vehicles.extend(list(EMPTY_VEHICLES_IN_REGION[near_idx]))
                                seen_subarea.append(near_idx)

                            if len(IDLE_VEHICLES_IN_REGION[near_idx]) != 0:
                                empty_vehicles.extend(list(IDLE_VEHICLES_IN_REGION[near_idx]))
                            if gap <= 0:
                                break
                    k += 1
                    if gap <= 0:
                        break
            assert len(users) == len(set(users))
            assert len(empty_vehicles) == len(set(empty_vehicles))

        if gap > 0:
            failures.append(more_orders_region)
            continue

        model = build_and_solve_model(empty_vehicles, partial_capacity_vehicles, users)
        parse_mip_and_dispatch(model, empty_vehicles, partial_capacity_vehicles, users, current_time)

    redundant_users = []
    if failures:
        users = []
        empty_vehicles = list(EMPTY_VEHICLES)
        partial_capacity_vehicles = list(PARTIAL_CAPACITY_VEHICLES)
        for more_orders_region in failures:
            for more_vehicle_subarea in more_orders_region[:-1]:
                users.extend(USERS_IN_REGION[more_vehicle_subarea])

        total_feasible_length = 2 * len(empty_vehicles) + len(partial_capacity_vehicles)
        while total_feasible_length < len(users):
            redundant_users.append(users.pop(random.randrange(len(users))))

        model = build_and_solve_model(empty_vehicles, partial_capacity_vehicles, users)
        parse_mip_and_dispatch(model, empty_vehicles, partial_capacity_vehicles, users, current_time)
    for area in USERS_IN_REGION.keys():
        USERS_IN_REGION[area] = set()

    return redundant_users
