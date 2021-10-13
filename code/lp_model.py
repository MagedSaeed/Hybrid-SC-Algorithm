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
            facility.is_open * facility.fixed_cost
            for facility in self.network.plants_echelon
        )
        FY = sum(
            facility.is_open * facility.fixed_cost
            for facility in self.network.warehouses_echelon
        )
        GZ = sum(
            facility.is_open * facility.fixed_cost
            for facility in self.network.distribution_centers_echelon
        )

        Xsit_coeffs = [
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

        Xsit_sum = lpSum(
            coeff * self.Xsit[(s, i, t)]
            for s, supplier in enumerate(Xsit_coeffs)
            for i, plant in enumerate(Xsit_coeffs[s])
            for t, coeff in enumerate(Xsit_coeffs[s][i])
        )

        Yijp_coeffs = [
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

        Yijp_sum = lpSum(
            coeff * self.Yijp[(i, p, j)]
            for i, plant in enumerate(Yijp_coeffs)
            for p, warehouse in enumerate(Yijp_coeffs[i])
            for j, coeff in enumerate(Yijp_coeffs[i][p])
        )

        Zjkp_coeffs = [
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

        Zjkp_sum = lpSum(
            coeff * self.Zjkp[(j, k, p)]
            for j, warehouse in enumerate(Zjkp_coeffs)
            for k, dist_center in enumerate(Zjkp_coeffs[j])
            for p, coeff in enumerate(Zjkp_coeffs[j][k])
        )

        Qkmp_coeffs = [
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

        Qkmp_sum = lpSum(
            coeff * self.Qkmp[(k, m, p)]
            for k, dist_center in enumerate(Qkmp_coeffs)
            for m, market in enumerate(Qkmp_coeffs[k])
            for p, coeff in enumerate(Qkmp_coeffs[k][m])
        )

        return EX + FY + GZ + Xsit_sum + Yijp_sum + Zjkp_sum + Qkmp_sum

    @property
    def Z2(self):
        net = self.network
        U_coeffs = [
            sum(
                [
                    material_prop_delivery_risk * material_delivery_risk_impact
                    + material_prop_quality_risk * material_quality_risk_impact
                    + material_prop_delivery_risk
                    * material_prop_quality_risk
                    * max(material_delivery_risk_impact, material_quality_risk_impact)
                    for material_prop_delivery_risk, material_delivery_risk_impact, material_prop_quality_risk, material_quality_risk_impact in zip(
                        supplier.prop_delivery_risk,
                        supplier.delivery_risk_impact,
                        supplier.prop_quality_risk,
                        supplier.quality_risk_impact,
                    )
                ]
            )
            for supplier in net.suppliers_echelon
        ]
        U = sum(
            Us.is_open * U_coeff for U_coeff, Us in zip(U_coeffs, net.suppliers_echelon)
        )
        # comment this code just in case Us is a decision variable solved by LP not by the Hybrid.
        # LpVariable.dicts(
        #     "Us",
        #     [Us for Us, supplier in enumerate(net.suppliers_echelon)],
        # )
        # prd_ird_prq_irq_U = lpSum(coeff * U[(s,)] for s, coeff in enumerate(U_coeffs))

        X_coeffs = [
            sum(
                [
                    product_prop_delivery_risk * product_delivery_risk_impact
                    + product_prop_quality_risk * product_quality_risk_impact
                    + product_prop_delivery_risk
                    * product_prop_quality_risk
                    * max(product_delivery_risk_impact, product_quality_risk_impact)
                    for product_prop_delivery_risk, product_delivery_risk_impact, product_prop_quality_risk, product_quality_risk_impact in zip(
                        plant.prop_delivery_risk,
                        plant.delivery_risk_impact,
                        plant.prop_quality_risk,
                        plant.quality_risk_impact,
                    )
                ]
            )
            for plant in net.plants_echelon
        ]
        X = sum(
            Xi.is_open * X_coeff for X_coeff, Xi in zip(X_coeffs, net.plants_echelon)
        )

        Y_coeffs = [
            sum(
                [
                    product_prop_delivery_risk * product_delivery_risk_impact
                    for product_prop_delivery_risk, product_delivery_risk_impact in zip(
                        warehouse.prop_delivery_risk,
                        warehouse.delivery_risk_impact,
                    )
                ]
            )
            for warehouse in net.warehouses_echelon
        ]
        Y = sum(
            Yj.is_open * Y_coeff
            for Y_coeff, Yj in zip(Y_coeffs, net.warehouses_echelon)
        )

        Z_coeffs = [
            sum(
                [
                    product_prop_delivery_risk * product_delivery_risk_impact
                    for product_prop_delivery_risk, product_delivery_risk_impact in zip(
                        dist_center.prop_delivery_risk,
                        dist_center.delivery_risk_impact,
                    )
                ]
            )
            for dist_center in net.distribution_centers_echelon
        ]
        Z = sum(
            Zk.is_open * Z_coeff
            for Z_coeff, Zk in zip(Z_coeffs, net.distribution_centers_echelon)
        )

        return U + X + Y + Z

    @property
    def Z3(self):
        net = self.network
        EFX = sum(X.opening_env_impact * X.is_open for X in net.plans_echelon)
        EWY = sum(Y.opening_env_impact * Y.is_open for Y in net.warehouses_echelon)
        EDZ = sum(
            Z.opening_env_impact * Z.is_open for Z in net.distribution_centers_echelon
        )
