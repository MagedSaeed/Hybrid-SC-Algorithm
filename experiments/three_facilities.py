from hybrid_algorithm import SupplyChainNetwork, LPModel, HybridAlgorithm
import random
import numpy as np

seed = 0

np.random.seed(seed)
random.seed(seed)

solutions_list = []

for i in range(1, 1001):
    print("#" * 100)
    print(f"optimizing {i} network".center(100, "#"))
    print("#" * 100)
    net = SupplyChainNetwork(
        facilities_count=3,
        raw_materials_count=4,
        markets_count=10,
        products_count=4,
    )
    net.initialize_random_network()
    net.apply_initial_greedy_solution()
    model = LPModel(net)
    hyb = HybridAlgorithm(
        network=net,
        tabu_size=5,
        T=50,
        Tf=1,
        alpha=0.9,
        K=0.5 * (3 * 4 + 10),
    )
    solutions_list.append(hyb.optimize())
# hyb.optimize()
