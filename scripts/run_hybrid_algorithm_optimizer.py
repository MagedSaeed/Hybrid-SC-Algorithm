import click
import random
import sys
import time
from supply_chain_network.config import AppConfig

import numpy as np

if "." not in sys.path:
    sys.path.append(".")
from supply_chain_network import SupplyChainNetwork
from supply_chain_network.optimizers import HybridAlgorithm, LPModel
from supply_chain_network.config import AppConfig
from supply_chain_network.optimizers.utils import Solution
from supply_chain_network.utils import get_three_random_weights


@click.command()
@click.option(
    "--config_path",
    default=None,
    help="Path to config file. If no config is provided, the default config will be used.",
    show_default=False,
)
@click.option(
    "--seed",
    default=1,
    type=int,
    help="Random seed used across the algorithm",
    show_default=True,
)
@click.option(
    "--tabu_size",
    default=7,
    type=int,
    help="Tabu Size",
    show_default=True,
)
@click.option(
    "-T",
    default=100,
    type=int,
    help="Initial Temperature",
    show_default=True,
)
@click.option(
    "-Tf",
    default=1,
    type=int,
    help="Final Temperature",
    show_default=True,
)
@click.option(
    "-a",
    "--alpha",
    default=0.9,
    type=float,
    help="alpha parameter",
    show_default=True,
)
@click.option(
    "-K",
    default=0.9,
    type=int,
    help="Number of iterations, K.",
    show_default=True,
)
@click.option(
    "--number_of_neighbors",
    default=None,
    type=int,
    required=False,
    help="Neighbors size. defaults to number of facilities * 4.",
)
@click.option(
    "--neighbors_percentage",
    default=0.3,
    type=float,
    help="Neighbors percentage",
    show_default=True,
)
@click.option(
    "-h",
    default=3,
    type=int,
    help="h value.",
    show_default=True,
)
def run_experiment(
    config_path,
    seed,
    tabu_size,
    t,
    tf,
    alpha,
    k,
    number_of_neighbors,
    neighbors_percentage,
    h,
):
    if config_path is None:
        config = AppConfig.config
    else:
        AppConfig.configure(config_file_path=config_path)
        config = AppConfig.config
    facilities_count = int(config["facilities"]["facilities_count"])
    if number_of_neighbors is None:
        number_of_neighbors = facilities_count * 4
    T, Tf, K = t, tf, k
    run(
        config,
        seed,
        tabu_size,
        T,
        Tf,
        alpha,
        K,
        number_of_neighbors,
        neighbors_percentage,
        h,
    )


def run(
    config,
    seed,
    tabu_size,
    T,
    Tf,
    alpha,
    K,
    number_of_neighbors,
    neighbors_percentage,
    h,
):
    np.random.seed(seed)
    random.seed(seed)

    facilities_count = int(config["facilities"]["facilities_count"])
    markets_count = int(config["facilities"]["markets_count"])
    products_count = int(config["facilities"]["products_count"])
    raw_materials_count = int(config["facilities"]["raw_materials_count"])
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
        h=h,
        number_of_neighbors=number_of_neighbors,
        neighbors_percentage=neighbors_percentage,
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
        normalized_hybrid_multi_objective_value = model.normalized_multi_objective_value
        weighted_multi_objective_value = model.weighted_multi_objective_value
        w1 = solution.meta_data["z1_weight"]
        w2 = solution.meta_data["z2_weight"]
        w3 = solution.meta_data["z3_weight"]
        print(
            f"""{solution_index},{tabu_size},{T},{Tf},{alpha},{K},{number_of_neighbors},{neighbors_percentage},{greedy_z1},{hybrid_z1},{normalized_hybrid_z1},{greedy_z2},{hybrid_z2},{normalized_hybrid_z2},{greedy_z3},{hybrid_z3},{normalized_hybrid_z3},{greedy_multi_objective_value},{hybrid_multi_objective_value},{normalized_hybrid_multi_objective_value},{w1},{w2},{w3},{weighted_multi_objective_value},{running_time},{solution}"""
        )


run_experiment()
