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
        EX = sum(
            facility.is_open * facility.fixed_cost for facility in net.plants_echelon
        )
        FY = sum(
            facility.is_open * facility.fixed_cost
            for facility in net.warehouses_echelon
        )
        GZ = sum(
            facility.is_open * facility.fixed_cost
            for facility in net.distribution_centers_echelon
        )

        X_coeffs = [
            [
                [
                    material_cost
                    + supplier.plants_distances[plant_index] * material_trans_cost
                    for material_trans_cost in supplier.material_trans_cost[plant_index]
                ]
                for plant_index, material_cost in zip(
                    supplier.material_trans_cost.keys(),
                    supplier.material_purchase_cost,
                )
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

        cc_cb_t_X = lpSum(
            coeff * X[(s, i, t)]
            for s, supplier in enumerate(X_coeffs)
            for i, plant in enumerate(X_coeffs[s])
            for t, coeff in enumerate(X_coeffs[s][i])
        )

        Y_coeffs = [
            [
                [
                    production_cost
                    + plant.warehouse_distances[warehouse_index] * product_trans_cost
                    for product_trans_cost in plant.products_trans_cost[warehouse_index]
                ]
                for warehouse_index, production_cost in zip(
                    plant.products_trans_cost.keys(),
                    plant.products_prod_cost,
                )
            ]
            for plant in net.plants_echelon
        ]

        Y = LpVariable.dicts(
            "Yijp",
            [
                (Yi, Yp, Yj)
                for Yi, plant in enumerate(net.plants_echelon)
                for Yp in plant.products_trans_cost
                for Yj in range(len(plant.products_trans_cost[Yp]))
            ],
        )

        cp_ct_t_Y = lpSum(
            coeff * Y[(i, p, j)]
            for i, plant in enumerate(Y_coeffs)
            for p, warehouse in enumerate(Y_coeffs[i])
            for j, coeff in enumerate(Y_coeffs[i][p])
        )

        Z_coeffs = [
            [
                [
                    warehouse.dist_centers_distances[dist_center_index]
                    * product_trans_cost
                    for product_trans_cost in warehouse.products_trans_cost[
                        dist_center_index
                    ]
                ]
                for dist_center_index in warehouse.products_trans_cost.keys()
            ]
            for warehouse in net.warehouses_echelon
        ]

        Z = LpVariable.dicts(
            "Zjkp",
            [
                (Zj, Zk, Zp)
                for Zj, warehouse in enumerate(net.warehouses_echelon)
                for Zk in warehouse.products_trans_cost
                for Zp in range(len(warehouse.products_trans_cost[Zk]))
            ],
        )

        cd_t_Z = lpSum(
            coeff * Z[(j, k, p)]
            for j, warehouse in enumerate(Z_coeffs)
            for k, dist_center in enumerate(Z_coeffs[j])
            for p, coeff in enumerate(Z_coeffs[j][k])
        )

        Q_coeffs = [
            [
                [
                    product_price
                    - dist_center.market_distances[market_index] * product_trans_cost
                    for product_trans_cost, product_price in zip(
                        dist_center.products_trans_cost[market_index],
                        dist_center.selling_prices[market_index],
                    )
                ]
                for market_index in dist_center.products_trans_cost.keys()
            ]
            for dist_center in net.distribution_centers_echelon
        ]

        Q = LpVariable.dicts(
            "Qkmp",
            [
                (Qk, Qm, Qp)
                for Qk, dist_center in enumerate(net.distribution_centers_echelon)
                for Qm in dist_center.products_trans_cost
                for Qp in range(len(dist_center.products_trans_cost[Qm]))
            ],
        )

        sp_co_t_Q = lpSum(
            coeff * Q[(k, m, p)]
            for k, dist_center in enumerate(Q_coeffs)
            for m, market in enumerate(Q_coeffs[k])
            for p, coeff in enumerate(Q_coeffs[k][m])
        )

        return EX + FY + GZ + cc_cb_t_X + cp_ct_t_Y + cd_t_Z + sp_co_t_Q
