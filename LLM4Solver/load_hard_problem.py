import os
import pandas as pd
from dataloader import parse_input, parse_solution, generate_prompt, write_dataframe_to_csv


def hard_dic(folder):
    datas, solutions = [], []
    data_path = os.path.join(folder, "data")
    solution_path = os.path.join(folder, 'solutions')

    for filename in os.listdir(data_path):
        temp_data_path = os.path.join(data_path, filename)
        temp_solution_path = os.path.join(solution_path, filename)

        datas.append(open(temp_data_path))
        solutions.append(open(temp_solution_path))
    return datas, solutions


def build_prompt(datas: list, solutions: list):
    prompts, all_gaps, all_objective_values = [], [], []
    for data, solution in zip(datas, solutions):
        prompt, gaps, objective_values = generate_prompt(solution, data, ascending=True,
                                                         descending=False, is_inference=False)
        if prompt is not False:
            prompts.append(prompt)
            all_gaps.append(gaps)
            all_objective_values.append(objective_values)
        prompt, gaps, objective_values = generate_prompt(solution, data, descending=True,
                                                         ascending=False, is_inference=False)

        if prompt is not False:
            prompts.append(prompt)
            all_gaps.append(gaps)
            all_objective_values.append(objective_values)

        prompt, gaps, objective_values = generate_prompt(solution, data, ascending=True,
                                                         descending=False, is_inference=False, is_random=True,
                                                         ratio=0.5)
        if prompt is not False:
            prompts.append(prompt)
            all_gaps.append(gaps)
            all_objective_values.append(objective_values)

        prompt, gaps, objective_values = generate_prompt(solution, data, descending=True,
                                                         ascending=False, is_inference=False, is_random=True,
                                                         ratio=0.5)

        if prompt is not False:
            prompts.append(prompt)
            all_gaps.append(gaps)
            all_objective_values.append(objective_values)
    df = pd.DataFrame({'prompt': prompts, 'gaps': all_gaps, 'objective_values': all_objective_values})
