from env import *
from components.user import User
import random
from utils.vehicle_update_behaviour import *
import multiprocessing
from multiprocessing import Manager


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
