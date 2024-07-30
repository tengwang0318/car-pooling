import json
import os
import random
from model_env import *
import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3.1-8B-Instruct")


def read_all_json_files(folder):
    category_dic = {}
    for category in os.listdir(folder):
        if os.path.isfile(os.path.join(folder, category)):
            continue
        if category == "hard":
            continue
        data_folder = os.path.join(folder, category, "data")
        solution_folder = os.path.join(folder, category, "solutions")
        temp_dic = {}
        temp_data = []
        temp_solution = []
        for data_path in os.listdir(data_folder):
            temp_path = os.path.join(data_folder, data_path)
            temp_data.append(json.load(open(temp_path)))
            # for solution_path in os.listdir(solution_folder):
            #     temp_path = os.path.join(solution_folder, solution_path)
            #     temp_solution.append(json.load(open(temp_path)))
            data_name = data_path.split(".")[0]
            solution_name = os.path.join(solution_folder, f'solution_{data_name}.json')
            temp_solution.append(json.load(open(solution_name)))

        temp_dic["data"] = temp_data
        temp_dic['solution'] = temp_solution

        category_dic[category] = temp_dic
    return category_dic


def parse_input(data):
    empty_vehicles, one_order_vehicles, users = "EMPTY VEHICLES: ", "ONE ORDER VEHICLES: ", "USERS: "
    for idx, (lat, lon) in enumerate(data['empty_vehicles']):
        empty_vehicles += f"({idx}) ({round(lat, 2)}, {round(lon, 2)}), "
    for idx, (lat, lon) in enumerate(data['one_order_vehicles']):
        one_order_vehicles += f"({idx}) ({round(lat, 2)}, {round(lon, 2)}), "
    for idx, (lat, lon) in enumerate(data['users']):
        users += f"({idx}) ({round(lat, 2)}, {round(lon, 2)}), "
    return "\n".join([empty_vehicles, one_order_vehicles, users])


def parse_solution(data):
    solutions = []
    gaps = []
    objective_values = []
    time = data[-1]['time']
    for data_ in data[:-1]:
        solution = data_['solution']

        x_s, y_s, z_s = [], [], []
        if "x" in solution:
            for x1, x2, _ in solution["x"]:
                x_s.append((x1, x2))
        if "y" in solution:
            for y1, y2, y3, _ in solution["y"]:
                y_s.append((y1, y2, y3))
        if "z" in solution:
            for z1, z2, _ in solution["z"]:
                z_s.append((z1, z2))
        x_text, y_text, z_text = "x: " if x_s else "", "y: " if y_s else "", "z: " if z_s else ""

        for x1, x2 in x_s:
            x_text += f"({x1}, {x2}) "
        for y1, y2, y3 in y_s:
            y_text += f"({y1}, {y2}, {y3}) "
        for z1, z2 in z_s:
            z_text += f"({z1}, {z2}) "

        text = "\n".join(
            [x_text, y_text, z_text]) + f"\ngap: {data_['gap']}, objective value: {data_['objective_value']}"
        gaps.append(data_['gap'])
        objective_values.append(data_['objective_value'])
        solutions.append(text)
    return solutions, time, gaps, objective_values


def generate_prompt(previous_solutions, model_data, is_inference=False, is_random=False, ascending=True,
                    descending=False, ratio=0):
    prompt = r"""Your task is to find the optimal solution for a carpool dispatch problem.
If you cannot find the optimal solution, you should try to return a better feasible solution.
The background is as follows:

### Rules for vehicle-order:
1. Each order is for one user only.
2. Each car can accept up to two orders.
3. There are three possible scenarios:
   1. Two people simultaneously hail a ride within a certain time range and decide to share the ride. The car will pick up Person A first, then Person B, and drop off Person A first, followed by Person B.
   2. A person willing to share a ride, Person A, is already in the car and the car has started the trip. A new carpool request from Person B is received. The car will go from its current location to pick up Person B, drop off Person A, and finally drop off Person B.
   3. A person takes a ride from start to finish without any carpooling.

The objective is to minimize the total Manhattan distance between vehicles and users, considering all segments of the vehicle paths:

$$
\min \sum_{i=1}^{n_1} \sum_{j=1}^{m} x_{ij} \cdot d_{ij} + \sum_{i=1}^{n_1} \sum_{j=1}^{m} \sum_{k=1, k \neq j}^{m} y_{ijk} \cdot (d_{ij} + d_{jk}') + \sum_{i=1}^{n_2} \sum_{j=1}^{m} z_{ij} \cdot d_{ij}''
$$

where:

- $x_{ij}$ is a decision variable indicating whether empty car $i$ is assigned to user $j$ (1 if yes, 0 if no).
- $y_{ijk}$ is a decision variable indicating whether empty car $i$ is assigned to pick up user $j$ and then user $k$ (1 if yes, 0 if no).
- $z_{ij}$ is a decision variable indicating whether car $i$ with one passenger willing to share is assigned to user $j$ (1 if yes, 0 if no).
- $d_{ij}$ is the Manhattan distance between vehicle $i$ and user $j$.
- $d_{jk}'$ is the Manhattan distance between user $j$ and user $k$.
- $d_{ij}''$ is the Manhattan distance between vehicle $i$ with one order and user $j$.

#### Constraints

The number of empty vehicles * 2 + the number of vehicles with one sharing order must be less than or equal to the number of incoming orders.

1. Every user is assigned to one vehicle:
   $$
   \sum_i x_{ij}+\sum_i\sum_{k,j\ne k} (y_{ijk } + y_{ikj})+\sum_{i'}z_{i',j}=1 \space, \forall \space j
   $$

2. Every empty vehicle picks up at most two people:
   $$
   \sum_j x_{ij} + \sum_j\sum_{k\ne j}y_{ijk}\le1, \forall i
   $$

3. Every vehicle with one passenger picks up at most one person:
   $$
   \sum_j z_{ij}\le 1,\forall i
   $$

4. Binary variables:
   $$
   z_{i',j}=0,1, \forall i',j
   $$

   $$
   x_{ij}=0,1, \forall i,j
   $$

   $$
   y_{ijk}=0,1, \forall i,j,k
   $$

You are given x and y coordinates (which are transformed from latitude and longitude using the Mercator projection method) for every empty vehicle, one-person vehicle, and user. The format is as follows:
EMPTY VEHICLES: (0) (x0, y0), (1) (x1, y1) ... # If no vehicles, use \n
ONE ORDER VEHICLES: (0) (x0, y0), (1) (x1, y1) ... # If no vehicles, use \n 
USERS: (0) (x0, y0), (1) (x1, y1) ... # If no users, use \n
After transforming the latitude and longitude into x and y, it's much easier to calculate the Manhattan distance between two places. The Manhattan distance between (x0, y0) and (x1, y1) = abs(x1-x0) + abs(y1-y0)
"""
    prompt += "\n" + parse_input(model_data) + '\n'

    prompt += r"""Below are some previous solutions, you can derive the optimal solution straightforwardly or derive the intermediate feasible solution step by step.
The term "gap" refers to the difference between the best known solution and the best possible solution (optimal solution) within a given tolerance. The smaller the gap, the better the feasible solution. The format of previous solutions is:

# Indices start from 0
x: (EMPTY_0, USER_5) (EMPTY_2, USER_3)... # Car whose index is 'EMPTY_0' is assigned to user whose index is 'USER_5', and so on.
y: (EMPTY_1, USER_1, USER_0) (EMPTY_3, USER_10, USER_9)... # Car whose index is 'EMPTY_1' picks up user whose index is 'USER_1', then user whose index is 'USER_0', and so on.
z: (ONE_REQUEST_0, USER_6), (ONE_REQUEST_1, USER_7)... # Car whose index is 'ONE_REQUEST_0' with one existing passenger picks up user whose index is 'USER_6', and so on.
If no one is assigned to a car alone, the x line is \n.
If no two people are assigned to share a car, the y line is \n.
If no one is assigned to a car with one existing passenger, the z line is \n.
"""

    solutions, time, gaps, objective_values = parse_solution(previous_solutions)

    current_length = len(tokenizer(prompt)['input_ids'])
    if current_length > MAX_LENGTH:
        return False, False, False

    # if is_random:
    #     length = len(solutions)
    #     N = max(1, int(length * ratio))
    #     indices = sorted(random.sample(range(1, length), N))
    #     solutions = [solutions[i] for i in indices]
    #     gaps = [gaps[i] for i in indices]
    #     objective_values = [objective_values[i] for i in indices]

    idx2length = {}
    template = "Solution {}:\n{}\n\n"

    max_length = len(solutions)

    for idx, solution in enumerate(solutions):
        idx2length[idx] = len(tokenizer(template.format(idx, solution))['input_ids'])

    if ascending:  # based on gap
        temp_text = ""
        idx = max_length - 1
        if current_length + idx2length[idx] <= MAX_LENGTH - MAX_LENGTH_GAP:
            return False, False, False
        while idx > 0 and current_length + idx2length[idx] <= MAX_LENGTH - MAX_LENGTH_GAP:
            current_length += idx2length[idx]
            temp_text = "one of solutions starts:\n" + solutions[idx] + "\none of solutions ends\n\n" + temp_text

            idx -= 1

        solutions = [solutions[i] for i in range(idx + 1, max_length)]
        gaps = [gaps[i] for i in range(idx + 1, max_length)]
        objective_values = [objective_values[i] for i in range(idx + 1, max_length)]
    elif descending:
        temp_text = ""
        idx = 1
        if current_length + idx2length[idx] <= MAX_LENGTH - MAX_LENGTH_GAP:
            return False, False, False
        while idx < max_length and current_length + idx2length[idx] <= MAX_LENGTH - MAX_LENGTH_GAP:
            current_length += idx2length[idx]
            temp_text = temp_text + "one of solutions starts:\n" + solutions[idx] + "\none of solutions ends\n\n"

            idx += 1
        solutions = [solutions[i] for i in range(1, idx)]
        gaps = [gaps[i] for i in range(1, idx)]
        objective_values = [objective_values[i] for i in range(1, idx)]

    prompt = prompt + temp_text
    if is_inference:
        prompt += r"""Return a JSON object that includes x, y, and z. 任何多余的文本都别输出. The format is as follows:
{
    "x": [[EMPTY_0, USER_5], [EMPTY_2, USER_3], ... ],
    "y": [[EMPTY_1, USER_1, USER_0], [EMPTY_3, USER_10, USER_9], ... ],
    "z": [[ONE_REQUEST_0, USER_6], [ONE_REQUEST_1, USER_7], ...]
}
The JSON object should only include entries where the corresponding binary variable (x_ij, y_ijk, or z_ij) equals 1. For example, if x_ij=1, then the list in x should include [i, j]. Similarly, include entries for y and z where y_ijk=1 and z_ij=1, respectively.
"""

    return prompt, gaps, objective_values


def write_dataframe_to_csv(df, filepath):
    mode = 'a' if os.path.exists(filepath) else 'w'
    header = not os.path.exists(filepath)
    df.to_csv(filepath, mode=mode, header=header, index=False)


def generate_dataset(path="/Users/code/simulator/lp",
                     is_from_gurobi=True,
                     train_outfile="/Users/code/simulator/data/train/train.csv",
                     valid_outfile="/Users/code/simulator/data/valid/valid.csv",
                     test_outfile="/Users/code/simulator/data/test/test.csv"):
    category_dic = read_all_json_files(path)
    prompts, all_gaps, all_objective_values = [], [], []
    if is_from_gurobi:
        for one_category_dic in category_dic.values():
            for previous_solutions, previous_data in zip(one_category_dic['solution'], one_category_dic['data']):
                prompt, gaps, objective_values = generate_prompt(previous_solutions, previous_data, ascending=True,
                                                                 descending=False, is_inference=False)
                if prompt is not False:
                    prompts.append(prompt)
                    all_gaps.append(gaps)
                    all_objective_values.append(objective_values)

                prompt, gaps, objective_values = generate_prompt(previous_solutions, previous_data, descending=True,
                                                                 ascending=False, is_inference=False)

                if prompt is not False:
                    prompts.append(prompt)
                    all_gaps.append(gaps)
                    all_objective_values.append(objective_values)
    else:
        for one_category_dic in category_dic.values():
            for previous_solutions, previous_data in zip(one_category_dic['solution'], one_category_dic['data']):
                prompt, gaps, objective_values = generate_prompt(previous_solutions, previous_data, is_inference=False,
                                                                 is_random=True, ratio=0.5)

                if prompt is not False:
                    prompts.append(prompt)
                    all_gaps.append(gaps)
                    all_objective_values.append(objective_values)

    df = pd.DataFrame({'prompt': prompts, 'gaps': all_gaps, 'objective_values': all_objective_values})

    train_df, temp_df = train_test_split(df, test_size=0.1, random_state=42)
    valid_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)

    write_dataframe_to_csv(train_df, train_outfile)
    write_dataframe_to_csv(valid_df, valid_outfile)
    write_dataframe_to_csv(test_df, test_outfile)


if __name__ == '__main__':
    generate_dataset(is_from_gurobi=True)
    # generate_dataset(is_from_gurobi=False)
