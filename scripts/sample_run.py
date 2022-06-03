import csv
import itertools
import random
import sys
import time

sys.path.append('.')
import numpy as np
from hybrid_algorithm import HybridAlgorithm, LPModel, SupplyChainNetwork
from hybrid_algorithm.config import AppConfig
from hybrid_algorithm.hybrid_algorithm.util import Solution
from hybrid_algorithm.utils import get_three_random_weights

AppConfig.configure(config_file_path="experiments/three_facilities/config.ini")

seed = 1

np.random.seed(seed)
random.seed(seed)

facilities_count = 5
markets_count = 20
products_count = 4
raw_materials_count = 4

N = facilities_count * 4 + markets_count


tabu_size = 5

T = 50
Tf = 1

alpha = 0.9

K = int(0.5 * N)


net = SupplyChainNetwork(
    facilities_count=facilities_count,
    raw_materials_count=raw_materials_count,
    markets_count=markets_count,
    products_count=products_count,
)
net.initialize_random_network()
net.apply_initial_greedy_solution()
w1, w2, w3 = 0.1, 0.1, 0.8
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
)
best_solution, intermediate_solutions = optimizer.optimize()
end_time = time.time()
running_time = round(end_time - start_time, 2)
if best_solution in intermediate_solutions:
    intermediate_solutions.remove(best_solution)
intermediate_solutions = sorted(
    intermediate_solutions,
    key=lambda solution: Solution.evaluate_solution_optimal(
        solution,
        net,
    ),
)
for solution_index, solution in enumerate(
    itertools.chain(
        [best_solution],
        intermediate_solutions,
    ),
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
    normalized_hybrid_multi_objective_value = model.normalized_multi_objective_value
    weighted_multi_objective_value = model.weighted_multi_objective_value
    print("-" * 100)
    print("greedy z1", greedy_z1)
    print("hybrid z1", hybrid_z1)
    print("greedy z2", greedy_z2)
    print("hybrid z2", hybrid_z2)
    print("greedy z3", greedy_z3)
    print("hybrid z3", hybrid_z3)
    print("greedy multi", greedy_multi_objective_value)
    print("weighted multi", weighted_multi_objective_value)
