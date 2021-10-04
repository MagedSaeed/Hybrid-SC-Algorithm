from pulp import LpMaximize, LpProblem, LpStatus, LpVariable, lpSum

# from supply_chain_network import SupplyChainNetwork

# network = SupplyChainNetwork.get_random_network()

# model = LpProblem(name="Z1", sense=LpMaximize)


# # ignore sp for the time being
# Qkmp = LpVariable.dicts(
#     "Qkmp", [(k, m, p) for k in range(3) for m in range(3) for p in range(3)]
# )
# Qkmp_sum = lpSum(Qkmp[(k, m, p)] for k in range(3) for m in range(3) for p in range(3))

# # ignore e for the time being

# Xsit = LpVariable.dicts(
#     "Xsit", [(s, i, t) for s in range(3) for i in range(3) for t in range(3)]
# )
# Xsit_sum = lpSum(Xsit[(s, i, t)] for s in range(3) for i in range(3) for t in range(3))

# Yijp = LpVariable.dicts(
#     "Yijp", [(i, j, p) for i in range(3) for j in range(3) for p in range(3)]
# )
# Yijp_sum = lpSum(Yijp[(i, j, p)] for i in range(3) for j in range(3) for p in range(3))

# Zjkp = LpVariable.dicts(
#     "Zjkp", [(j, k, p) for j in range(3) for k in range(3) for p in range(3)]
# )
# Zjkp_sum = lpSum(Zjkp[(j, k, p)] for j in range(3) for k in range(3) for p in range(3))

# Xi = LpVariable.dicts("Xi", [i for i in range(3)])
# Xi_sum = lpSum(Xi[i] for i in range(3))

# Yj = LpVariable.dicts("Yj", [j for j in range(3)])
# Yj_sum = lpSum(Yj[j] for j in range(3))

# Zk = LpVariable.dicts("Zk", [k for k in range(3)])
# Zk_sum = lpSum(Zk[k] for k in range(3))


# objective_function = Qkmp_sum - ()


# model += objective_function


class LPModel:
    def __init__(self, network):
        self.network = network

    @property
    def Z1(self):
        net = self.network
        Q = LpVariable.dicts(
            "Qkmp",
            [
                (Qk, Qm, Qp)
                for Qk, center in enumerate(net.distribution_centers_echelon)
                for Qm in center.products_trans_cost.keys()
                for Qp in range(len(center.products_trans_cost[Qm]))
            ],
        )
        sp_Q = lpSum(
            price * Q[(center_index, Qm, Qp_index)]
            for center_index, center in enumerate(net.distribution_centers_echelon)
            for Qm in center.products_trans_cost.keys()
            for Qp_index, price in enumerate(center.products_trans_cost[Qm])
        )
        EX = sum(
            facility.is_open * facility.fixed_cost for facility in net.plants_echelon
        )
        FY = sum(
            facility.is_open * facility.fixed_cost
            for facility in net.warehouses_echelon
        )
        FY = sum(
            facility.is_open * facility.fixed_cost
            for facility in net.distribution_centers_echelon
        )

        X_coeffs = [
            [
                [
                    supplier.material_purchase_cost[plant_index]
                    + supplier.plants_distances[plant_index] * material_trans_cost
                    for material_trans_cost in supplier.material_trans_cost[plant_index]
                ]
                for plant_index in supplier.material_trans_cost.keys()
            ]
            for supplier in net.suppliers_echelon
        ]

        X = LpVariable.dicts(
            "Xsit",
            [
                (Xs, Xi, Xt)
                for Xs, supplier in enumerate(net.suppliers_echelon)
                for Xt in supplier.material_trans_cost
                for Xi in range(len(supplier.material_trans_cost[Xt]))
            ],
        )

        cc_cb_tX = lpSum(
            coeff * X[(s, i, t)]
            for s, supplier in enumerate(X_coeffs)
            for i, plant in enumerate(X_coeffs[s])
            for t, coeff in enumerate(X_coeffs[s][i])
        )
