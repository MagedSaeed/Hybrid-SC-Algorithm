from hybrid_algorithm import SupplyChainNetwork, LPModel
import random
import numpy as np
from hybrid_algorithm.config import AppConfig
from os.path import dirname, abspath

current_directory = dirname(abspath(__file__))

AppConfig.configure(config_file_path=f"{current_directory}/config.ini")
config = AppConfig.config

seed = 0

np.random.seed(seed)
random.seed(seed)

facilities_count = int(config["facilities"]["facilities_count"])
markets_count = int(config["facilities"]["markets_count"])
products_count = int(config["facilities"]["products_count"])
raw_materials_count = int(config["facilities"]["raw_materials_count"])

N = facilities_count * products_count + markets_count

max_neighbors = facilities_count ** 4
print("max neighbors:", max_neighbors)

max_iterations = 10 ** 4
print("finding Zmax & Zmin. Max iterations is:", max_iterations)


def find_Zmax_min(objective):
    solutions_list = list()
    for _ in range(max_iterations):
        net = SupplyChainNetwork(
            facilities_count=facilities_count,
            raw_materials_count=raw_materials_count,
            markets_count=markets_count,
            products_count=products_count,
        )
        net.initialize_random_network()
        net.apply_initial_greedy_solution()
        model = LPModel(net)
        solution_value = getattr(model, objective)
        if not solution_value:
            # some networks may not be applicable especially for small facilities sizes
            print("could not find a solution")
            continue
        solutions_list.append(solution_value)
    print(f"max value for {objective} is", max(solutions_list))
    print(f"min value for {objective} is", min(solutions_list))


find_Zmax_min(objective="Z1_objective_value")
find_Zmax_min(objective="Z2_objective_value")
find_Zmax_min(objective="Z3_objective_value")
find_Zmax_min(objective="multi_objective_value")
