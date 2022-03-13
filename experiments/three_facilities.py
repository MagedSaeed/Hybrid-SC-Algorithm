from hybrid_algorithm.supply_chain_network import SupplyChainNetwork
from hybrid_algorithm.lp_model import LPModel
from hybrid_algorithm import HybridAlgorithm

from hybrid_algorithm.config import AppConfig

AppConfig.configure(config_file_path="./experiments/config.py")

net = SupplyChainNetwork()
net.apply_initial_greedy_solution()
model = LPModel(net)
hyb = HybridAlgorithm(net)
hyb.optimize()
