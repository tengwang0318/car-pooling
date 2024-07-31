import os
import json
import shutil
import time

import gurobipy as gp
from gurobipy import GRB
from collections import defaultdict

CNT = 1


def load_all_category(folder_path="/Users/code/simulator/lp"):
    categories = []
    for temp_folder in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, temp_folder)):
            continue
        categories.append(os.path.join(folder_path, temp_folder))
    return categories


def parse_json_and_filter_hard_problem(folder_path):
    file_paths = []
    solution_folder_path = os.path.join(folder_path, "solutions")
    for json_file in os.listdir(solution_folder_path):
        left, right = json_file.index("_"), json_file.index(".")
        cnt = json_file[left + 1:right]
        json_path = os.path.join(solution_folder_path, json_file)
        json_obj = json.load(open(json_path))
        # print(json_obj)
        if json_obj[-2]['gap'] > 0.001:
            data_path = os.path.join(folder_path, "data", f"{cnt}.json")
            lp_path = os.path.join(folder_path, f"{cnt}.lp")
            # file_paths.append((data_path, json_path, lp_path))
            file_paths.append((data_path, lp_path))
    return file_paths


def collect_all_hard_problem(folder_path="/Users/code/simulator/lp"):
    all_hard_problems = []
    categories = load_all_category(folder_path)
    for category in categories:
        all_hard_problems.extend(parse_json_and_filter_hard_problem(category))
    return all_hard_problems


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


def move_hard_problems():
    global CNT
    data_path_template = "hard/data/{}.json"
    lp_path_template = "hard/data/{}.lp"
    all_hard_problems = collect_all_hard_problem()
    for data_path, lp_path in all_hard_problems:
        shutil.move(data_path, data_path_template.format(CNT))
        shutil.move(lp_path, lp_path_template.format(CNT))

        solve_lp(lp_path, CNT)

        CNT += 1


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


def solve_lp(lp_file, cnt):
    log_path = "hard/log/{}.log".format(cnt)
    solution_path = 'hard/solutions/{}.json'.format(cnt)
    start_time = time.time()
    model = gp.read(lp_file)
    model.setParam("LogFile", log_path)
    model.setParam(GRB.Param.TimeLimit, 1200)
    model.setParam(GRB.Param.MIPGap, 0.01)
    model.optimize(my_callback)
    end_time = time.time()

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


if __name__ == '__main__':
    move_hard_problems()
