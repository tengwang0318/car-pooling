import json
import math
import time

import gurobipy as gp
from gurobipy import GRB
from collections import defaultdict
from env import *


def lat_lon_to_xy(lat, lon):
    R = 6371.0

    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

    x = R * lon_rad
    y = R * math.log(math.tan(math.pi / 4 + lat_rad / 2))

    return round(x - 11474.16255996467, 2), round(y - 3537.118802722021, 2)


def manhattan_distance(lat1, lon1, lat2, lon2):
    x1, y1 = lat_lon_to_xy(lat1, lon1)
    x2, y2 = lat_lon_to_xy(lat2, lon2)
    return abs(x1 - x2) + abs(y1 - y2)


def generate_json(empty_vehicles, one_order_vehicles, users):
    empty_list = [lat_lon_to_xy(v.latitude, v.longitude) for v in empty_vehicles]
    one_order_list = [lat_lon_to_xy(v.latitude, v.longitude) for v in one_order_vehicles]
    user_list = [lat_lon_to_xy(u.start_latitude, u.start_longitude) for u in users]
    data = {
        "empty_vehicles": empty_list,
        "one_order_vehicles": one_order_list,
        "users": user_list,
    }
    return json.dumps(data)


def parse_and_store_var(var, value, dic):
    if "x" in var.varName:
        num1, num2 = var.varName[var.varName.index("[") + 1:var.varName.index("]")].split(",")
        dic['x'].append((int(num1), int(num2), value))
    elif "y" in var.varName:
        num1, num2, num3 = var.varName[var.varName.index("[") + 1:var.varName.index("]")].split(",")
        dic['y'].append((int(num1), int(num2), int(num3), value))
    else:
        num1, num2 = var.varName[var.varName.index("[") + 1:var.varName.index("]")].split(",")
        dic['z'].append((int(num1), int(num2), value))


intermediate_solutions = []


def my_callback(model, where):
    if where == gp.GRB.Callback.MIPSOL:
        solution = model.cbGetSolution(model.getVars())
        current_gap = model.cbGet(gp.GRB.Callback.MIPSOL_OBJBST) - model.cbGet(gp.GRB.Callback.MIPSOL_OBJBND)
        relative_gap = abs(current_gap) / (1e-10 + abs(model.cbGet(gp.GRB.Callback.MIPSOL_OBJBST)))

        intermediate_solution = defaultdict(list)
        for var, value in zip(model.getVars(), solution):
            if value != 0:
                parse_and_store_var(var, value, intermediate_solution)

        objective_value = model.cbGet(gp.GRB.Callback.MIPSOL_OBJBST)

        intermediate_solutions.append({
            "solution": intermediate_solution,
            "gap": relative_gap,
            "objective_value": objective_value
        })


def build_and_solve_model(empty_vehicles, one_order_vehicles, users):
    model = gp.Model("vehicle_routing")

    n_vehicles = len(empty_vehicles)
    n_users = len(users)
    n_one_order_vehicles = len(one_order_vehicles)
    start_time = time.time()
    d = {}
    d_prime = {}
    d_double_prime = {}

    for i in range(n_vehicles):
        for j in range(n_users):
            d[i, j] = manhattan_distance(empty_vehicles[i].latitude, empty_vehicles[i].longitude,
                                         users[j].start_latitude, users[j].start_longitude)

    for j in range(n_users):
        for k in range(n_users):
            if j != k:
                d_prime[j, k] = manhattan_distance(users[j].start_latitude, users[j].start_longitude,
                                                   users[k].start_latitude, users[k].start_longitude)

    for i in range(n_one_order_vehicles):
        for j in range(n_users):
            d_double_prime[i, j] = manhattan_distance(users[j].start_latitude, users[j].start_longitude,
                                                      one_order_vehicles[i].latitude, one_order_vehicles[i].longitude)

    x = model.addVars(n_vehicles, n_users, vtype=GRB.BINARY, name="x")
    y = model.addVars(n_vehicles, n_users, n_users, vtype=GRB.BINARY, name="y")
    z = model.addVars(n_one_order_vehicles, n_users, vtype=GRB.BINARY, name="z")

    model.setObjective(
        gp.quicksum(x[i, j] * d[i, j] for i in range(n_vehicles) for j in range(n_users)) +
        gp.quicksum((d[i, j] + d_prime[j, k]) * y[i, j, k] for i in range(n_vehicles) for j in range(n_users) for k in
                    range(n_users) if j != k) +
        gp.quicksum(d_double_prime[z_i, j] * z[z_i, j] for z_i in range(n_one_order_vehicles) for j in range(n_users)),
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

    lp_path, log_path, data_path, solution_path = lp_filepath()
    model.setParam("LogFile", log_path)
    initial_time_limit = ENV['gurobi_run_time_for_simulation']
    model.setParam(GRB.Param.TimeLimit, initial_time_limit)
    model.optimize(my_callback)
    end_time = time.time()

    # Check if the initial time limit was reached
    if model.status == GRB.Status.TIME_LIMIT:
        print("Initial time limit reached. Extending the time limit and/or setting a relative gap target.")
        additional_time_limit = 600  # additional time in seconds (e.g., 10 minutes)
        model.setParam(GRB.Param.TimeLimit, additional_time_limit)
        model.setParam(GRB.Param.MIPGap, 0.50)  # set the relative gap to 10%
        model.optimize(my_callback)

    json_data = generate_json(empty_vehicles, one_order_vehicles, users)
    model.write(lp_path)

    with open(data_path, "w") as f:
        f.write(json_data)

    final_solution = defaultdict(list)
    for v in model.getVars():
        if v.X > 0:
            parse_and_store_var(v, v.X, final_solution)

    final_gap = model.MIPGap
    objective_value = model.ObjVal

    intermediate_solutions.append({
        "solution": final_solution,
        "gap": final_gap,
        "objective_value": objective_value
    })

    intermediate_solutions.append({"time": end_time - start_time})
    with open(solution_path, "w") as f:
        json.dump(intermediate_solutions, f, indent=4)

    while intermediate_solutions:
        intermediate_solutions.pop()
    return model
