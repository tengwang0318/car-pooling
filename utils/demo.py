import math
import gurobipy as gp
from gurobipy import GRB


class Vehicle:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude


class User:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude


def manhattan_distance(lat1, lon1, lat2, lon2):
    # km_per_degree_lat = 111
    # lat1_rad = math.radians(lat1)
    # lat2_rad = math.radians(lat2)
    #
    # delta_lat = abs(lat2 - lat1)
    # delta_lon = abs(lon2 - lon1)
    #
    # dist_lat = delta_lat * km_per_degree_lat
    # dist_lon = delta_lon * km_per_degree_lat * math.cos((lat1_rad + lat2_rad) / 2)
    #
    # manhattan_dist = dist_lat + dist_lon

    # return manhattan_dist
    return abs(lat2 - lat1) + abs(lon2 - lon1)


def build_model(empty_vehicles, one_order_vehicles, users):
    # Initialize the model
    model = gp.Model("vehicle_routing")

    # Parameters
    n_vehicles = len(empty_vehicles)
    n_users = len(users)
    n_one_order_vehicles = len(one_order_vehicles)

    # Distances
    d = {}
    d_prime = {}
    d_double_prime = {}

    for i in range(n_vehicles):
        for j in range(n_users):
            d[i, j] = manhattan_distance(empty_vehicles[i].latitude, empty_vehicles[i].longitude, users[j].latitude,
                                         users[j].longitude)

    for j in range(n_users):
        for k in range(n_users):
            if j != k:
                d_prime[j, k] = manhattan_distance(users[j].latitude, users[j].longitude, users[k].latitude,
                                                   users[k].longitude)

    for i in range(n_one_order_vehicles):
        for j in range(n_users):
            d_double_prime[i, j] = manhattan_distance(users[j].latitude, users[j].longitude,
                                                      one_order_vehicles[i].latitude,
                                                      one_order_vehicles[i].longitude)

    # Decision variables
    x = model.addVars(n_vehicles, n_users, vtype=GRB.BINARY, name="x")
    y = model.addVars(n_vehicles, n_users, n_users, vtype=GRB.BINARY, name="y")
    z = model.addVars(n_one_order_vehicles, n_users, vtype=GRB.BINARY, name="z")

    # Objective function
    model.setObjective(
        gp.quicksum(x[i, j] * d[i, j] for i in range(n_vehicles) for j in range(n_users)) +
        gp.quicksum((d[i, j] + d_prime[j, k]) * y[i, j, k] for i in range(n_vehicles) for j in range(n_users) for k in
                    range(n_users) if j != k) +
        gp.quicksum(
            (d_double_prime[z_i, j] * z[z_i, j] for z_i in range(n_one_order_vehicles) for j in range(n_users))),
        GRB.MINIMIZE
    )
    # Constraints
    for j in range(n_users):
        model.addConstr(
            gp.quicksum(x[i, j] for i in range(n_vehicles)) +
            gp.quicksum(y[i, j, k] for i in range(n_vehicles) for k in range(n_users) if j != k) +
            gp.quicksum(y[i, k, j] for i in range(n_vehicles) for k in range(n_users) if j != k) +
            gp.quicksum(z[z_i, j] for z_i in range(n_one_order_vehicles)) == 1,
            f"constr1_{j}"
        )

    for i in range(n_vehicles):
        model.addConstr(
            gp.quicksum(x[i, j] for j in range(n_users)) +
            gp.quicksum(y[i, j, k] for j in range(n_users) for k in range(n_users) if j != k) <= 1,
            f"constr2_{i}"
        )

    for z_i in range(n_one_order_vehicles):
        model.addConstr(
            gp.quicksum(z[z_i, j] for j in range(n_users)) <= 1,
            f"constr3_{z_i}"
        )

    return model


# Example usage
empty_vehicles = [
    Vehicle(100, 30),
    Vehicle(100, 28),
    Vehicle(30, 30)
]
users = [
    User(100, 28),
    User(100, 29),
    User(100, 29.5),
    User(30, 27),
    User(105, 30),

]
one_order_vehicles = [
    Vehicle(102, 30)
]

model = build_model(empty_vehicles, one_order_vehicles, users)
model.optimize()

# Output the results
for v in model.getVars():
    # print(v.varName, v.x)
    if v.x > 0:
        # print(f"{v.varName}: {v.x}")
        if "x" in v.varName:
            left, right = v.varName.index("["), v.varName.index("]")
            num1, num2 = v.varName[left + 1:right].split(",")
            print(f"x: {num1} -> {num2}")
        elif "y" in v.varName:
            left, right = v.varName.index("["), v.varName.index("]")
            num1, num2, num3 = v.varName[left + 1:right].split(",")
            print(f"y: {num1} -> {num2} -> {num3}")
        else:
            left, right = v.varName.index("["), v.varName.index("]")
            num1, num2 = v.varName[left + 1:right].split(",")
            print(f"z: {num1} -> {num2}")

print(f"Objective value: {model.objVal}")
