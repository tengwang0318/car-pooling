"""
{
   "x": [[EMPTY_0, USER_5], [EMPTY_2, USER_3], ... ],
   "y": [[EMPTY_1, USER_1, USER_0], [EMPTY_3, USER_10, USER_9], ... ],
   "z": [[ONE_REQUEST_0, USER_6], [ONE_REQUEST_1, USER_7], ...]
}
"""


def manhattan_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)


def calculate_objective_value(solution_dic: dict, model_data):
    cost = 0
    n_empty_vehicles = len(model_data.get("empty_vehicles", 0))
    n_one_order_vehicles = len(model_data.get("one_order_vehicles", 0))
    n_users = len(model_data.get("users", 0))
    x = [[0] * n_users for _ in range(n_empty_vehicles)]
    y = [[[0] * n_users for _ in range(n_users)] for _ in range(n_empty_vehicles)]

    z = [[0] * n_users for _ in range(n_one_order_vehicles)]

    for i in range(n_empty_vehicles):
        for j in range(n_users):
            x[i][j] = manhattan_distance(model_data['empty_vehicles'][i][0], model_data['empty_vehicles'][i][1],
                                         model_data['users'][j][0], model_data['users'][j][1])
    for i in range(n_empty_vehicles):
        for j in range(n_users):
            for k in range(n_users):
                if j == k:
                    continue
                y[i][j][k] = manhattan_distance(model_data['empty_vehicles'][i][0],
                                                model_data['empty_vehicles'][i][1],
                                                model_data['users'][j][0],
                                                model_data['users'][j][1]) + manhattan_distance(
                    model_data['users'][j][0], model_data['users'][j][1],
                    model_data['users'][k][0], model_data['users'][k][1]
                )
    for i in range(n_one_order_vehicles):
        for j in range(n_users):
            z[i][j] = manhattan_distance(model_data['one_order_vehicles'][i][0],
                                         model_data['one_order_vehicles'][i][0],
                                         model_data['users'][j][0],
                                         model_data['users'][j][1])

    if 'x' in solution_dic:
        for i, j, _ in solution_dic['x']:
            cost += x[i][j]
            print(cost)
    if "y" in solution_dic:
        for i, j, k, _ in solution_dic['y']:
            cost += y[i][j][k]
            print(cost)
    if "z" in solution_dic:
        for i, j, _ in solution_dic['z']:
            cost += z[i][j]
            print(cost)
    return cost
