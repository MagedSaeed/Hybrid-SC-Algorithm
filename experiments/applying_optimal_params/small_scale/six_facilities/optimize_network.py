import os
import csv
import random
import sys
import time

import numpy as np

if "." not in sys.path:
    sys.path.append(".")
    
from os.path import dirname, abspath
from supply_chain_network import SupplyChainNetwork
from supply_chain_network.optimizers import HybridAlgorithm, LPModel
from supply_chain_network.config import AppConfig
from supply_chain_network.optimizers.utils import Solution
from supply_chain_network.utils import get_three_random_weights
from scripts.network_exporter.export import NetworkExporter
from experiments.applying_optimal_params.small_scale.optimal_params import K,T,Tf,tabu_size,alpha,neighbor_percentage


current_directory = dirname(abspath(__file__))


config = AppConfig.config

RANDOM_SEED = 1

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


facilities_count = 6
markets_count = 20
products_count = 4
raw_materials_count = 4


net = SupplyChainNetwork(
    facilities_count=facilities_count,
    raw_materials_count=raw_materials_count,
    markets_count=markets_count,
    products_count=products_count,
)
net.initialize_random_network()


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
    tabu_size=tabu_size,
    network=net,
    T=T,
    Tf=Tf,
    alpha=alpha,
    K=K,
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



csv_dir = f'{current_directory}/csv'
excel_dir = f'{current_directory}/excel'

os.system(f'mkdir -p {csv_dir}')
os.system(f'mkdir -p {excel_dir}')

exporter = NetworkExporter(network=net,output_path=csv_dir)
exporter.export()
NetworkExporter.convert_directory_csv_files_to_xlxs(input_directory=csv_dir,output_directory=excel_dir)