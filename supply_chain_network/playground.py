# this file contains examples on how to use the package
from supply_chain_network.optimizers import LPModel, HybridAlgorithm
from supply_chain_network import SupplyChainNetwork

net = SupplyChainNetwork()
net.apply_initial_greedy_solution()
model = LPModel(net)
model.multi_objective_value
hyb = HybridAlgorithm(net)
hyb.optimize()
