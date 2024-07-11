from env import *
from components.user import User
import random
from utils.vehicle_update_behaviour import *

def random_dispatch(current_users: list[User]):
    while current_users:
        temp_user = current_users.pop()
        temp_vehicle = random.choice(list(EMPTY_VEHICLES))
        try:
            vehicle_update_for_one_user(vehicle=temp_vehicle,
                                        user=temp_user)
            print(f"Vehicle {temp_vehicle.ID} 去接 {temp_user.user_id}")
            break
        except Exception as e:

            print(e)
            current_users.append(temp_user)

            continue

