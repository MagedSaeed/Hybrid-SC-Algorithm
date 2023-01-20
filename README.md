# Hybrid-SC-Algorithm

This repository contains an implementation to a proposed algorithm to optimize supply chains. This novel algorithm is a hybridization  of three well-known algorithms: Neighborhood-Structures, Simulated Annealing, and Tabu Search. Further details about this algorithm and its implementation can be found in this file: [https://github.com/MagedSaeed/Hybrid-SC-Algorithm/blob/main/A%20hybrid%20algorithm%20fot%20SC%20design.PDF]

# Architecture

The framework contains two major components, the network definiation and the hybrid algorithm implementation.

The network defination contains a set of data classes to collect the values of each facilities. The framework also supports random initialization for these values for experimentation setups.

The second major component is the algorithm implementaiton as described in the paper. This implemenation depends on two main modules. The first one is the linear programming solver module, named as `lp_model.py`, and the second one is the VNS module which is used to find the nighbor solutions, i.e. to make a step twoards the optimal solution.

The following picture overviews this software architecture. A full example is provided twords the end of this file in the `getting started` section.


 <p align="center"> 
 <img src = "https://raw.githubusercontent.com/MagedSaeed/Hybrid-SC-Algorithm/main/software_architecture.drawio.png"/>
 </p>

# Requirements:

- CPLEX [https://www.ibm.com/products/ilog-cplex-optimization-studio/cplex-optimizer]
- This project works on `python3.8` as this is a dependency of the current CPLEX [CPLEX_Studio201] version.


# Installation

Before installing this package, please note that this package depends on [CPLEX](https://www.ibm.com/products/ilog-cplex-optimization-studio/cplex-optimizer) solver through [PulP](https://github.com/coin-or/pulp). You can still install other solvers and change the code to use it. 

As the package is written in Python. It is installable through pip directly from this repository: 

```
pip install git+https://github.com/MagedSaeed/Hybrid-SC-Algorithm
```

# Getting Started

After installing the package, you may start with the following code to generate the optimal values for the three objective functions as specified in the paper.

```python
# this file contains examples on how to use the package

# get the LPModel and the hybrid algorithm
from supply_chain_network.optimizers import LPModel, HybridAlgorithm

from supply_chain_network import SupplyChainNetwork

from pulp import GLPK # in case of not using CPLEX solver

# define the supply chain network characteristics

facilities_count = 3
raw_materials_count = 4
markets_count = 10
products_count = 4

network = SupplyChainNetwork(
        facilities_count=facilities_count,
        raw_materials_count=raw_materials_count,
        markets_count=markets_count,
        products_count=products_count,
    )

# initialize the network echelons randomly

network.initialize_random_network()

# apply the initial greedy solution
network.apply_initial_greedy_solution()

# evaluate the greedy solution
model = LPModel(network, solver=GLPK(msg=False)) # if solver argument is not passed, CPLEX will be used by default

# instantiate the algorithm optimizer
hybrid_optimizer = HybridAlgorithm(network)

# optimize with default values and get the solutions
best_solution, intermediate_solutions = hybrid_optimizer.optimize()

# evaluate the best solution:
network.apply_solution(best_solution)

model = LPModel(network, solver=GLPK(msg=False))

hybrid_z1 = model.Z1_objective_value
normalized_hybrid_z1 = model.Z1_normalized_objective_value

hybrid_z2 = model.Z2_objective_value
normalized_hybrid_z2 = model.Z2_normalized_objective_value

hybrid_z3 = model.Z3_objective_value
normalized_hybrid_z3 = model.Z3_normalized_objective_value

hybrid_multi_objective_value = model.multi_objective_value
normalized_hybrid_multi_objective_value = model.normalized_multi_objective_value

weighted_multi_objective_value = model.weighted_multi_objective_value

print(
    'Hybrid Z1:',hybrid_z1,
    'Normalized Hybrid Z1:', normalized_hybrid_z1,
)
print(
    'Hybrid Z2:',hybrid_z2,
    'Normalized Hybrid Z2:', normalized_hybrid_z2,
)
print(
    'Hybrid Z3:',hybrid_z3,
    'Normalized Hybrid Z3:', normalized_hybrid_z3,
)
print(
    'Hybrid Multi-objective Value:', hybrid_multi_objective_value,
    'Normalized Hybrid Multi-objective Value:', normalized_hybrid_multi_objective_value,
)
print(
    'Weighted Multi-objective Value:', weighted_multi_objective_value,
)

```

#Liscence

This implementation is under MIT liscense


# Contribution

Any contribution is welcomed for this project.

