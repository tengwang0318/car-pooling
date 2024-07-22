from env import *
from components.request import Request


def calculate_cost_for_finished_request(vehicle, request: Request):
    if request.users:
        users = request.users
        for user in users:
            user.cost += request.request_total_distance * ENV["money_per_meter"] / len(request.users)
        if request.is_dropoff_request:
            vehicle.dropoff_distance += request.request_total_distance
        vehicle.total_distance += request.request_total_distance

    if request.is_pickup_request:
        vehicle.pickup_distance += request.request_total_distance


def calculate_cost_for_unfinished_request(vehicle, request: Request, current_distance,
                                          previous_distance_high_bound):
    if request.users:
        users = request.users
        for user in users:
            user.cost += (current_distance - previous_distance_high_bound) * ENV["money_per_meter"] / len(request.users)
        vehicle.dropoff_distance += current_distance - previous_distance_high_bound
        vehicle.total_distance += current_distance - previous_distance_high_bound
        # vehicle.total_distance += current_distance - previous_distance_high_bound
