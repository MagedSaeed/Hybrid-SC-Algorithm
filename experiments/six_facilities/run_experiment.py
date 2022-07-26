import csv
import random
import sys
import time

import numpy as np

if "." not in sys.path:
    sys.path.append(".")
from hybrid_algorithm import HybridAlgorithm, LPModel, SupplyChainNetwork
from hybrid_algorithm.config import AppConfig
from hybrid_algorithm.hybrid_algorithm.util import Solution
from hybrid_algorithm.utils import get_three_random_weights
from os.path import dirname, abspath

current_directory = dirname(abspath(__file__))

AppConfig.configure(config_file_path=f"{current_directory}/config.ini")
config = AppConfig.config

seed = 1

np.random.seed(seed)
random.seed(seed)

facilities_count = int(config["facilities"]["facilities_count"])
markets_count = int(config["facilities"]["markets_count"])
products_count = int(config["facilities"]["products_count"])
raw_materials_count = int(config["facilities"]["raw_materials_count"])

N = facilities_count * products_count + markets_count


tabu_sizes = [5, 7, 15]

T_values = [50, 200, 300]

Tf_values = [1, 20, 50]

alpha_values = [0.9, 0.95, 0.99]

K_values = [int(0.5 * N), int(0.75 * N), N]

number_of_neighbors = facilities_count * 4

neighbors_percentages = [0.1, 0.2, 0.3]

results_file = open(
    f"{current_directory}/results.csv",
    "w",
    encoding="UTF8",
)

results_writer = csv.writer(results_file)

# write the headers of the results csv file
headers = [
    "solution index",
    "tabu size",
    "T",
    "Tf",
    "alpha",
    "K",
    "total neighbors",
    "neighbor_percentage",
    "greedy Z1",
    "hybrid Z1",
    "normalized hybrid Z1",
    "greedy Z2",
    "hybrid Z2",
    "normalized hybrid Z2",
    "greedy Z3",
    "hybrid Z3",
    "normalized hybrid Z3",
    "greedy multi objective value",
    "hybrid multi objective value",
    "normalized hybrid multi objective value",
    "w1",
    "w2",
    "w3",
    "weighted multi objective value",
    "optimization running time",
    "open/close status of facilities",
]
results_writer.writerow(headers)

net = SupplyChainNetwork(
    facilities_count=facilities_count,
    raw_materials_count=raw_materials_count,
    markets_count=markets_count,
    products_count=products_count,
)
net.initialize_random_network()

for tabu_size in tabu_sizes:
    for T in T_values:
        for Tf in Tf_values:
            for alpha in alpha_values:
                for K in K_values:
                    for neighbor_percentage in neighbors_percentages:
                        net.apply_initial_greedy_solution()
                        w1, w2, w3 = get_three_random_weights()
                        AppConfig.config["lp_model"]["z1_weight"] = str(w1)
                        AppConfig.config["lp_model"]["z2_weight"] = str(w2)
                        AppConfig.config["lp_model"]["z3_weight"] = str(w3)
                        model = LPModel(net)
                        greedy_z1 = model.Z1_objective_value
                        greedy_z2 = model.Z2_objective_value
                        greedy_z3 = model.Z3_objective_value
                        greedy_multi_objective_value = model.multi_objective_value
                        start_time = time.time()
                        optimizer = HybridAlgorithm(
                            network=net,
                            T=T,
                            Tf=Tf,
                            alpha=alpha,
                            K=K,
                            number_of_neighbors=number_of_neighbors,
                            neighbors_percentage=neighbor_percentage,
                        )
                        best_solution, intermediate_solutions = optimizer.optimize()
                        end_time = time.time()
                        running_time = round(end_time - start_time, 2)
                        intermediate_solutions = sorted(
                            intermediate_solutions,
                            key=lambda solution: Solution.evaluate_solution_optimal(
                                solution,
                                net,
                            ),
                        )
                        if best_solution not in intermediate_solutions:
                            intermediate_solutions.insert(0, best_solution)
                        for solution_index, solution in enumerate(
                            intermediate_solutions,
                            start=1,
                        ):
                            net.apply_solution(solution)
                            model = LPModel(net)
                            hybrid_z1 = model.Z1_objective_value
                            normalized_hybrid_z1 = model.Z1_normalized_objective_value
                            hybrid_z2 = model.Z2_objective_value
                            normalized_hybrid_z2 = model.Z2_normalized_objective_value
                            hybrid_z3 = model.Z3_objective_value
                            normalized_hybrid_z3 = model.Z3_normalized_objective_value
                            hybrid_multi_objective_value = model.multi_objective_value
                            normalized_hybrid_multi_objective_value = (
                                model.normalized_multi_objective_value
                            )
                            weighted_multi_objective_value = (
                                model.weighted_multi_objective_value
                            )
                            w1 = solution.meta_data["z1_weight"]
                            w2 = solution.meta_data["z2_weight"]
                            w3 = solution.meta_data["z3_weight"]
                            results_writer.writerow(
                                [
                                    solution_index,
                                    tabu_size,
                                    T,
                                    Tf,
                                    alpha,
                                    K,
                                    number_of_neighbors,
                                    neighbor_percentage,
                                    greedy_z1,
                                    hybrid_z1,
                                    normalized_hybrid_z1,
                                    greedy_z2,
                                    hybrid_z2,
                                    normalized_hybrid_z2,
                                    greedy_z3,
                                    hybrid_z3,
                                    normalized_hybrid_z3,
                                    greedy_multi_objective_value,
                                    hybrid_multi_objective_value,
                                    normalized_hybrid_multi_objective_value,
                                    w1,
                                    w2,
                                    w3,
                                    weighted_multi_objective_value,
                                    running_time,
                                    solution,
                                ]
                            )
                        print("#" * 100)
                        print("#" * 100)
                        print(
                            "done with tabu size:",
                            tabu_size,
                            "T:",
                            T,
                            "Tf:",
                            Tf,
                            "alpha",
                            alpha,
                            "K",
                            K,
                            "neighbors percentage",
                            neighbor_percentage,
                            f"in {running_time} seconds",
                        )
                        print("#" * 100)
                        print("#" * 100)
results_file.close()
