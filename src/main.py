from lp_model import LPModel
from supply_chain_network import SupplyChainNetwork

net = SupplyChainNetwork()
net.apply_initial_greedy_solution()
model = LPModel(net)
