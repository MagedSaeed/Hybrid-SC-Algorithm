from lp_model import LPModel
from supply_chain_network import SupplyChainNetwork
from hybrid_algorithm.core import HybridAlgorithm

net = SupplyChainNetwork()
net.apply_initial_greedy_solution()
model = LPModel(net)
model.multi_objective_value
hyb = HybridAlgorithm(net)
hyb.optimize()
