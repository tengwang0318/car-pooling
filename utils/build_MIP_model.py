import math
import gurobipy as gp
from gurobipy import GRB
from components.vehicle import Vehicle
from components.user import User


def manhattan_distance(lat1, lon1, lat2, lon2):
    km_per_degree_lat = 111
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    delta_lat = abs(lat2 - lat1)
    delta_lon = abs(lon2 - lon1)

    dist_lat = delta_lat * km_per_degree_lat
    dist_lon = delta_lon * km_per_degree_lat * math.cos((lat1_rad + lat2_rad) / 2)

    manhattan_dist = dist_lat + dist_lon

    return manhattan_dist


def build_model_for_more_car(vehicles: list[Vehicle], users: list[User]):
    model = gp.Model("VehicleUserAssignment")

    # Indices
    num_vehicles = len(vehicles)
    num_users = len(users)

    # Decision variables
    x = model.addVars(num_vehicles, num_users, vtype=GRB.BINARY, name="x")

    # Objective: Minimize the total distance between vehicles and users
    model.setObjective(gp.quicksum(
        x[i, j] * manhattan_distance(vehicles[i].latitude, vehicles[i].longitude, users[j].start_latitude,
                                     users[j].start_longitude)
        for i in range(num_vehicles) for j in range(num_users)
    ), GRB.MINIMIZE)

    # Constraints
    # Each vehicle should have at most one user
    model.addConstrs((gp.quicksum(x[i, j] for j in range(num_users)) <= 1 for i in range(num_vehicles)),
                     name="VehicleCapacity")

    # Each user should be assigned to exactly one vehicle
    model.addConstrs((gp.quicksum(x[i, j] for i in range(num_vehicles)) == 1 for j in range(num_users)),
                     name="UserAssignment")

    model.optimize()

    if model.status == GRB.OPTIMAL:
        assignment = {}
        for i in range(num_vehicles):
            for j in range(num_users):
                if x[i, j].X > 0.5:
                    assignment[vehicles[i]] = users[j]
                    break
        return assignment
    else:
        return None


def build_model(vehicles: list[Vehicle], users: list[User]):
    model = gp.Model("VehicleUserAssignment")

    # Indices
    num_vehicles = len(vehicles)
    num_users = len(users)

    # Decision variables
    x = model.addVars(num_vehicles, num_users, vtype=GRB.BINARY, name="x")

    # Objective: Minimize the total distance between vehicles and users
    model.setObjective(gp.quicksum(
        x[i, j] * manhattan_distance(vehicles[i].latitude, vehicles[i].longitude, users[j].start_latitude,
                                     users[j].start_longitude)
        for i in range(num_vehicles) for j in range(num_users)
    ), GRB.MINIMIZE)

    # Constraints
    # Each vehicle must be assigned to exactly one user
    model.addConstrs((gp.quicksum(x[i, j] for j in range(num_users)) == 1 for i in range(num_vehicles)),
                     name="VehicleAssignment")

    # Each user can be assigned to at most one vehicle
    model.addConstrs((gp.quicksum(x[i, j] for i in range(num_vehicles)) <= 1 for j in range(num_users)),
                     name="UserAssignment")

    model.optimize()

    if model.status == GRB.OPTIMAL:
        assignment = {}
        for i in range(num_vehicles):
            for j in range(num_users):
                if x[i, j].X > 0.5:
                    assignment[vehicles[i]] = users[j]
                    break
        return assignment
    else:
        return None
