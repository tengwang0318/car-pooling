import os
import json

DATA_CNT = 1
JSON_CNT = 1


def load_all_category(folder_path="/Users/code/simulator/lp"):
    categories = []
    for temp_folder in os.listdir(folder_path):
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
        if json_obj[-2]['gap'] > 0:
            data_path = os.path.join(folder_path, "data", f"{cnt}.json")
            file_paths.append((data_path, json_path))
    return file_paths


print(parse_json_and_filter_hard_problem("/Users/code/simulator/lp/RESOLUTION_8_TIME_60_data20161101"))
