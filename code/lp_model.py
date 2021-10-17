from functools import cached_property

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

    @cached_property
    def Qkmp(self):
        Qkmp = LpVariable.dicts(
            "Qkmp",
            [
                (Qk, Qm, Qp)
                for Qk, dist_center in enumerate(
                    self.network.distribution_centers_echelon
                )
                for Qm in dist_center.products_trans_cost
                for Qp in range(len(dist_center.products_trans_cost[Qm]))
            ],
            lowBound=0,
        )
        return Qkmp

    @cached_property
    def Xsit(self):
        Xsit = LpVariable.dicts(
            "Xsit",
            [
                (Xs, Xi, Xt)
                for Xs, supplier in enumerate(self.network.suppliers_echelon)
                for Xt in supplier.material_trans_cost
                for Xi in range(len(supplier.material_trans_cost[Xt]))
            ],
            lowBound=0,
        )
        return Xsit

    @cached_property
    def Yijp(self):
        Yijp = LpVariable.dicts(
            "Yijp",
            [
                (Yi, Yp, Yj)
                for Yi, plant in enumerate(self.network.plants_echelon)
                for Yp in plant.products_trans_cost
                for Yj in range(len(plant.products_trans_cost[Yp]))
            ],
            lowBound=0,
        )
        return Yijp

    @cached_property
    def Zjkp(self):
        Zjkp = LpVariable.dicts(
            "Zjkp",
            [
                (Zj, Zk, Zp)
                for Zj, warehouse in enumerate(self.network.warehouses_echelon)
                for Zk in warehouse.products_trans_cost
                for Zp in range(len(warehouse.products_trans_cost[Zk]))
            ],
            lowBound=0,
        )
        return Zjkp

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
                    + plant.warehouses_distances[warehouse_index] * product_trans_cost
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
        EFX = sum(X.opening_env_impact * X.is_open for X in net.plants_echelon)
        EWY = sum(Y.opening_env_impact * Y.is_open for Y in net.warehouses_echelon)
        EDZ = sum(
            Z.opening_env_impact * Z.is_open for Z in net.distribution_centers_echelon
        )

        Xsit_coeffs = [
            [
                [
                    material_impact * plant_distance
                    for material_impact in supplier.material_trans_env_impact[
                        plant_index
                    ]
                ]
                for plant_index, plant_distance in enumerate(supplier.plants_distances)
            ]
            for supplier in self.network.suppliers_echelon
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
                    product_env_impact + product_trans_impact * warehouse_distance
                    for product_trans_impact, product_env_impact in zip(
                        plant.products_trans_env_impact[warehouse_index],
                        plant.products_env_impact,
                    )
                ]
                for warehouse_index, warehouse_distance in enumerate(
                    plant.warehouses_distances
                )
            ]
            for plant in net.plants_echelon
        ]

        Yijp_sum = lpSum(
            coeff * self.Yijp[(i, p, j)]
            for i, plant in enumerate(Yijp_coeffs)
            for j, warehouse in enumerate(Yijp_coeffs[i])
            for p, coeff in enumerate(Yijp_coeffs[i][j])
        )

        Zjkp_coeffs = [
            [
                [
                    product_impact * dist_center_distance
                    for product_impact in warehouse.products_trans_env_impact[
                        dist_center_index
                    ]
                ]
                for dist_center_index, dist_center_distance in enumerate(
                    warehouse.dist_centers_distances,
                )
            ]
            for warehouse in self.network.warehouses_echelon
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
                    product_impact * market_distance
                    for product_impact in dist_center.products_trans_env_impact[
                        market_index
                    ]
                ]
                for market_index, market_distance in enumerate(
                    dist_center.market_distances
                )
            ]
            for dist_center in self.network.distribution_centers_echelon
        ]

        Qkmp_sum = lpSum(
            coeff * self.Qkmp[(k, m, p)]
            for k, dist_center in enumerate(Qkmp_coeffs)
            for m, market in enumerate(Qkmp_coeffs[k])
            for p, coeff in enumerate(Qkmp_coeffs[k][m])
        )

        return EFX + EWY + EDZ + Yijp_sum + Xsit_sum + Zjkp_sum + Qkmp_sum

    @cached_property
    def constrains(self):
        net = self.network
        constrains = list()

        Q = self.Qkmp
        X = self.Xsit
        Y = self.Yijp
        Z = self.Zjkp

        for m, market in enumerate(net.markets_echelon):
            for p, demand in enumerate(market.products_demand):
                """(4) constrain"""
                constrain = (
                    lpSum(
                        Q[k, m, p]
                        for k, dist_center in enumerate(
                            net.distribution_centers_echelon
                        )
                    )
                    == demand
                )
                constrains.append(constrain)

        for s, supplier in enumerate(net.suppliers_echelon):
            for t, capacity in enumerate(supplier.material_capacity):
                """(5) constrain"""
                constrain = (
                    lpSum(X[s, i, t] for i, plant in enumerate(net.plants_echelon))
                    <= supplier.is_open * capacity
                )
                constrains.append(constrain)

        for i, plant in enumerate(net.plants_echelon):
            for p, capacity in enumerate(plant.product_capacity):
                for raw_material in supplier.raw_materials:
                    """(6) constrain"""
                    wx_sum = lpSum(
                        raw_material.products_yields[p] * X[s, i, t]
                        for s, supplier in enumerate(net.suppliers_echelon)
                    )
                    constrain = wx_sum <= plant.is_open * capacity
                    constrains.append(constrain)
                    """(9) constrain"""
                    constrain = wx_sum == lpSum(
                        Y[i, j, p] for j, warehouse in enumerate(net.warehouses_echelon)
                    )
                    constrains.append(constrain)

        for j, warehouse in enumerate(net.warehouses_echelon):
            for p, capacity in enumerate(warehouse.product_capacity):
                """(7) constrain"""
                y_sum = lpSum(Y[i, j, p] for i, plant in enumerate(net.plants_echelon))
                constrain = y_sum <= warehouse.is_open * capacity
                constrains.append(constrain)
                """(10) constrain"""
                constrain = y_sum == lpSum(
                    Z[j, k, p]
                    for k, dist_center in enumerate(net.distribution_centers_echelon)
                )
                constrains.append(constrain)

        for k, dist_center in enumerate(net.distribution_centers_echelon):
            for p, capacity in enumerate(dist_center.product_capacity):
                """(8) constrain"""
                z_sum = lpSum(
                    dist_center.is_open * Z[j, k, p]
                    for j, warehouse in enumerate(net.warehouses_echelon)
                )
                constrain = z_sum <= dist_center.is_open * capacity

                constrains.append(constrain)
                """(11) constrain"""
                constrain = z_sum == lpSum(
                    Q[k, m, p] for m, market in enumerate(net.markets_echelon)
                )
                constrains.append(constrain)

        return constrains
