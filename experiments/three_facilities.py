from hybrid_algorithm import SupplyChainNetwork, LPModel, HybridAlgorithm


net = SupplyChainNetwork(
    facilities_count=3,
    raw_materials_count=4,
    markets_count=6,
    products_count=3,
)
net.initialize_random_network()
net.apply_initial_greedy_solution()
model = LPModel(net)
hyb = HybridAlgorithm(net)
hyb.optimize()
