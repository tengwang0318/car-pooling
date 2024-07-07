from env import *
from components.request import Request


def calculate_cost_for_finished_request(request: Request):
    if request.users:
        users = request.users
        for user in users:
            user.cost += request.request_total_distance * ENV["money_per_meter"] / len(
                request.users)


def calculate_cost_for_unfinished_request(request: Request, current_distance, previous_distance_high_bound):
    if request.users:
        users = request.users
        for user in users:
            user.cost += (current_distance - previous_distance_high_bound) * ENV["money_per_meter"] / len(request.users)
