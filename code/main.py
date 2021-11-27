# from supply_chain_network import SupplyChainNetwork

# network = SupplyChainNetwork.get_random_network()
# network.get_initial_solution()
# network.descripe()


from data_classes import SupplyChainNetwork
from lp_model import LPModel

net = SupplyChainNetwork()
net.apply_initial_greedy_solution()
model = LPModel(net)
