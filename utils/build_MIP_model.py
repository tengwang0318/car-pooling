import math
import gurobipy as gp
from gurobipy import GRB
from env import *


def manhattan_distance(lat1, lon1, lat2, lon2):
    km_per_degree_lat = 111
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    delta_lat = abs(lat2 - lat1)
    delta_lon = abs(lon2 - lon1)

    dist_lat = delta_lat * km_per_degree_lat
    dist_lon = delta_lon * km_per_degree_lat * math.cos((lat1_rad + lat2_rad) / 2)

    manhattan_dist = dist_lat + dist_lon

    return round(manhattan_dist, 2)


def build_and_solve_model(empty_vehicles, one_order_vehicles, users):
    model = gp.Model("vehicle_routing")

    n_vehicles = len(empty_vehicles)
    n_users = len(users)
    n_one_order_vehicles = len(one_order_vehicles)

    d = {}
    d_prime = {}
    d_double_prime = {}

    for i in range(n_vehicles):
        for j in range(n_users):
            d[i, j] = manhattan_distance(empty_vehicles[i].latitude, empty_vehicles[i].longitude,
                                         users[j].start_latitude,
                                         users[j].start_longitude)

    for j in range(n_users):
        for k in range(n_users):
            if j != k:
                d_prime[j, k] = manhattan_distance(users[j].start_latitude, users[j].start_longitude,
                                                   users[k].start_latitude, users[k].start_longitude)

    for i in range(n_one_order_vehicles):
        for j in range(n_users):
            d_double_prime[i, j] = manhattan_distance(users[j].start_latitude, users[j].start_longitude,
                                                      one_order_vehicles[i].latitude,
                                                      one_order_vehicles[i].longitude)

    x = model.addVars(n_vehicles, n_users, vtype=GRB.BINARY, name="x")
    y = model.addVars(n_vehicles, n_users, n_users, vtype=GRB.BINARY, name="y")
    z = model.addVars(n_one_order_vehicles, n_users, vtype=GRB.BINARY, name="z")

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
    model.write(lp_filepath())
    model.optimize()

    return model
