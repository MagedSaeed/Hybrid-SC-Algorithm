from pulp import LpMaximize, LpProblem, LpStatus, LpVariable, lpSum

from supply_chain_network import SupplyChainNetwork

network = SupplyChainNetwork.get_random_network()

model = LpProblem(name="Z1", sense=LpMaximize)


# ignore sp for the time being
Qkmp = LpVariable.dicts(
    "Qkmp", [(k, m, p) for k in range(3) for m in range(3) for p in range(3)]
)
Qkmp_sum = lpSum(Qkmp[(k, m, p)] for k in range(3) for m in range(3) for p in range(3))

# ignore e for the time being

Xsit = LpVariable.dicts(
    "Xsit", [(s, i, t) for s in range(3) for i in range(3) for t in range(3)]
)
Xsit_sum = lpSum(Xsit[(s, i, t)] for s in range(3) for i in range(3) for t in range(3))

Yijp = LpVariable.dicts(
    "Yijp", [(i, j, p) for i in range(3) for j in range(3) for p in range(3)]
)
Yijp_sum = lpSum(Yijp[(i, j, p)] for i in range(3) for j in range(3) for p in range(3))

Zjkp = LpVariable.dicts(
    "Zjkp", [(j, k, p) for j in range(3) for k in range(3) for p in range(3)]
)
Zjkp_sum = lpSum(Zjkp[(j, k, p)] for j in range(3) for k in range(3) for p in range(3))

Xi = LpVariable.dicts("Xi", [i for i in range(3)])
Xi_sum = lpSum(Xi[i] for i in range(3))

Yj = LpVariable.dicts("Yj", [j for j in range(3)])
Yj_sum = lpSum(Yj[j] for j in range(3))

Zk = LpVariable.dicts("Zk", [k for k in range(3)])
Zk_sum = lpSum(Zk[k] for k in range(3))


objective_function = Qkmp_sum - ()


model += objective_function
