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
    km_per_degree_lat = 111
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    delta_lat = abs(lat2 - lat1)
    delta_lon = abs(lon2 - lon1)

    dist_lat = delta_lat * km_per_degree_lat
    dist_lon = delta_lon * km_per_degree_lat * math.cos((lat1_rad + lat2_rad) / 2)

    manhattan_dist = dist_lat + dist_lon

    return manhattan_dist

def build_model(empty_vehicles, one_user_vehicles, users):
    n1 = len(empty_vehicles)  # number of empty cars
    n2 = len(one_user_vehicles)  # number of cars with one passenger willing to share
    m = len(users)  # number of users

    model = gp.Model("vehicle_dispatch")

    x = model.addVars(n1, m, vtype=GRB.BINARY, name="x")
    y = model.addVars(n1, m, m, vtype=GRB.BINARY, name="y")
    z = model.addVars(n2, m, vtype=GRB.BINARY, name="z")
    b = model.addVars(n1, vtype=GRB.BINARY, name="b")

    d_ij = [[manhattan_distance(empty_vehicles[i].latitude, empty_vehicles[i].longitude, users[j].latitude,
                                users[j].longitude) for j in range(m)] for i in range(n1)]
    d_jk_prime = [
        [manhattan_distance(users[j].latitude, users[j].longitude, users[k].latitude, users[k].longitude) for k in
         range(m)] for j in range(m)]
    d_ij_double_prime = [[manhattan_distance(one_user_vehicles[i].latitude, one_user_vehicles[i].longitude,
                                             users[j].latitude, users[j].longitude) for j in range(m)] for i in
                         range(n2)]
    print(d_ij)
    print(d_jk_prime)
    print(d_ij_double_prime)
    model.setObjective(
        gp.quicksum(x[i, j] * d_ij[i][j] for i in range(n1) for j in range(m)) +
        gp.quicksum(
            y[i, j, k] * (d_ij[i][j] + d_jk_prime[j][k]) for i in range(n1) for j in range(m) for k in range(m) if
            j != k) +
        gp.quicksum(z[i, j] * d_ij_double_prime[i][j] for i in range(n2) for j in range(m)),
        GRB.MINIMIZE
    )

    # Constraints
    # Each empty car either not assigned to any user or assigned to exactly two users
    model.addConstrs(
        (gp.quicksum(y[i, j, k] for j in range(m) for k in range(m) if j != k) == 2 * b[i] for i in range(n1)),
        "empty_car_assignment")

    # Each empty car can be assigned to at most one user directly
    model.addConstrs((gp.quicksum(x[i, j] for j in range(m)) <= 1 for i in range(n1)), "empty_car_one_user")

    # Each car with one passenger willing to share can be assigned to at most one user
    model.addConstrs((gp.quicksum(z[i, j] for j in range(m)) <= 1 for i in range(n2)), "car_one_sharing")

    # Each user must be assigned to exactly one vehicle
    model.addConstrs(
        (gp.quicksum(x[i, j] for i in range(n1)) +
         gp.quicksum(y[i, j, k] for i in range(n1) for k in range(m) if j != k) +
         gp.quicksum(y[i, k, j] for i in range(n1) for k in range(m) if j != k) +
         gp.quicksum(z[i, j] for i in range(n2)) == 1 for j in range(m)),
        "user_one_vehicle"
    )

    # Each empty car must be assigned to at least one user if it is used
    model.addConstrs((gp.quicksum(x[i, j] for j in range(m)) + gp.quicksum(
        y[i, j, k] for j in range(m) for k in range(m) if j != k) >= b[i] for i in range(n1)), "car_at_least_one_user")

    # Linearization constraints for y_ijk
    model.addConstrs((y[i, j, k] <= x[i, j] for i in range(n1) for j in range(m) for k in range(m) if j != k),
                     "linearization1")
    model.addConstrs((y[i, j, k] <= x[i, k] for i in range(n1) for j in range(m) for k in range(m) if j != k),
                     "linearization2")
    model.addConstrs(
        (y[i, j, k] >= x[i, j] + x[i, k] - 1 for i in range(n1) for j in range(m) for k in range(m) if j != k),
        "linearization3")

    # Optimize the model
    model.optimize()

    # Print the results
    if model.status == GRB.OPTIMAL:
        print("Optimal objective value:", model.objVal)
        for v in model.getVars():
            if v.x > 1e-6:
                print(f"{v.varName} = {v.x}")

    # Save the model
    model.write("vehicle_dispatch.lp")

def generate_demo_data():
    empty_vehicles = [
        Vehicle(latitude=30.5, longitude=114.5),

    ]

    one_user_vehicles = [
        Vehicle(latitude=100.1, longitude=114.1)
    ]

    users = [
        User(latitude=30.5, longitude=114.45),
        User(latitude=30.5, longitude=114.48),
    ]

    return empty_vehicles, one_user_vehicles, users

# Generate demo data and build the model
empty_vehicles, one_user_vehicles, users = generate_demo_data()
build_model(empty_vehicles, one_user_vehicles, users)
