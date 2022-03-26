from hybrid_algorithm import SupplyChainNetwork, HybridAlgorithm, LPModel
import random
import numpy as np
import csv

from hybrid_algorithm.config import AppConfig

AppConfig.configure(config_file_path="experiments/three_facilities/config.ini")

seed = 0

np.random.seed(seed)
random.seed(seed)

facilities_count = 3
markets_count = 10
products_count = 4
raw_materials_count = 4

N = facilities_count * 4 + markets_count


tabu_sizes = [5, 7, 15]

T_values = [50, 200, 300]
Tf_values = [1, 20, 50]

alpha_values = [0.9, 0.95, 0.99]

K_values = [int(0.5 * N), int(0.75 * N), N]

results_file = open(
    "experiments/three_facilities/results.csv",
    "w",
    encoding="UTF8",
)

results_writer = csv.writer(results_file)

# write the headers of the results csv file
headers = [
    "tabu size",
    "T",
    "Tf",
    "alpha",
    "K",
    "initial Z1",
    "optimized Z1",
    "normalized optimized Z1",
    "initila Z2",
    "optimized Z2",
    "normalized optimized Z2",
    "initila Z3",
    "optimized Z3",
    "normalized optimized Z3",
    "initila multi objective value",
    "optimized multi objective value",
    "normalized optimized multi objective value",
]
results_writer.writerow(headers)

for tabu_size in tabu_sizes:
    for T in T_values:
        for Tf in Tf_values:
            for alpha in alpha_values:
                for K in K_values:
                    net = SupplyChainNetwork(
                        facilities_count=facilities_count,
                        raw_materials_count=raw_materials_count,
                        markets_count=markets_count,
                        products_count=products_count,
                    )
                    net.initialize_random_network()
                    net.apply_initial_greedy_solution()
                    model = LPModel(net)
                    initial_z1 = model.Z1_objective_value
                    initial_z2 = model.Z2_objective_value
                    initial_z3 = model.Z3_objective_value
                    initial_multi_objective_value = model.multi_objective_value
                    optimizer = HybridAlgorithm(
                        network=net,
                        T=T,
                        Tf=Tf,
                        alpha=alpha,
                        K=K,
                    )
                    solution = optimizer.optimize()
                    net.apply_solution(solution)
                    model = LPModel(net)
                    optimized_z1 = model.Z1_objective_value
                    normalized_optimized_z1 = model.Z1_normalized_objective_value
                    optimized_z2 = model.Z2_objective_value
                    normalized_optimized_z2 = model.Z2_normalized_objective_value
                    optimized_z3 = model.Z3_objective_value
                    normalized_optimized_z3 = model.Z3_normalized_objective_value
                    optimized_multi_objective_value = model.multi_objective_value
                    normalized_optimized_multi_objective_value = (
                        model.normalized_multi_objective_value
                    )
                    results_writer.writerow(
                        [
                            tabu_size,
                            T,
                            Tf,
                            alpha,
                            K,
                            initial_z1,
                            optimized_z1,
                            normalized_optimized_z1,
                            initial_z2,
                            optimized_z2,
                            normalized_optimized_z2,
                            initial_z3,
                            optimized_z3,
                            normalized_optimized_z3,
                            initial_multi_objective_value,
                            optimized_multi_objective_value,
                            normalized_optimized_multi_objective_value,
                        ]
                    )
results_writer.close()
