from functools import cached_property
import copy
from utils import exclude_closed_facilities

from pulp import GLPK, LpMaximize, LpProblem, LpVariable, lpSum, CPLEX_PY


class LPModel:
    def __init__(self, network):
        self.network = copy.deepcopy(network)
        self.network = exclude_closed_facilities(self.network)

    @cached_property
    def Qkmp(self):
        Qkmp = LpVariable.dicts(
            "Qkmp",
            [
                (k, m, p)
                for k, dist_center in enumerate(
                    self.network.distribution_centers_echelon
                )
                for m, market_trans_cost in enumerate(dist_center.products_trans_cost)
                for p, product_trans_cost in enumerate(
                    dist_center.products_trans_cost[m]
                )
            ],
            lowBound=0,
        )
        return Qkmp

    @cached_property
    def Xsit(self):
        Xsit = LpVariable.dicts(
            "Xsit",
            [
                (s, i, t)
                for s, supplier in enumerate(self.network.suppliers_echelon)
                for i, plant_trans_cost in enumerate(supplier.material_trans_cost)
                for t, material_trans_cost in enumerate(supplier.material_trans_cost[i])
            ],
            lowBound=0,
        )
        return Xsit

    @cached_property
    def Yijp(self):
        Yijp = LpVariable.dicts(
            "Yijp",
            [
                (i, j, p)
                for i, plant in enumerate(self.network.plants_echelon)
                for j, warehouse_trans_cost in enumerate(plant.products_trans_cost)
                for p, product_trans_cost in enumerate(plant.products_trans_cost[j])
            ],
            lowBound=0,
        )
        return Yijp

    @cached_property
    def Zjkp(self):
        Zjkp = LpVariable.dicts(
            "Zjkp",
            [
                (j, k, p)
                for j, warehouse in enumerate(self.network.warehouses_echelon)
                for k, dist_center_trans_cost in enumerate(
                    warehouse.products_trans_cost
                )
                for p, product_trans_cost in enumerate(warehouse.products_trans_cost[k])
            ],
            lowBound=0,
        )
        return Zjkp

    @property
    def Z1(self):
        net = self.network
        EX = sum(facility.fixed_cost for facility in self.network.plants_echelon)
        FY = sum(facility.fixed_cost for facility in self.network.warehouses_echelon)
        GZ = sum(
            facility.fixed_cost
            for facility in self.network.distribution_centers_echelon
        )

        Xsit_coeffs = [
            [
                [
                    (
                        material_cost
                        + supplier.plants_distances[plant_index] * material_trans_cost
                    )
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
                    (
                        production_cost
                        + plant.warehouses_distances[warehouse_index]
                        * product_trans_cost
                    )
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
            coeff * self.Yijp[(i, j, p)]
            for i, plant in enumerate(Yijp_coeffs)
            for j, warehouse in enumerate(Yijp_coeffs[i])
            for p, coeff in enumerate(Yijp_coeffs[i][j])
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
                    (
                        product_price
                        - dist_center.market_distances[market_index]
                        * product_trans_cost
                    )
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

        return Qkmp_sum - (EX + FY + GZ + Xsit_sum + Yijp_sum + Zjkp_sum)

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
            coeff * self.Yijp[(i, j, p)]
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
                    >= demand
                )
                constrains.append(constrain)

        for s, supplier in enumerate(net.suppliers_echelon):
            # for t, capacity in enumerate(supplier.material_capacity):
            """(5) constrain"""
            constrain = (
                lpSum(
                    X[s, i, t]
                    for i, plant in enumerate(net.plants_echelon)
                    for t, capacity in enumerate(supplier.material_capacity)
                )
                <= supplier.capacity.sum()
            )
            constrains.append(constrain)

        for i, plant in enumerate(net.plants_echelon):
            # for p, capacity in enumerate(plant.product_capacity):
            """(6) constrain"""
            wx_sum = lpSum(
                raw_material.products_yields[p] * X[s, i, t]
                for s, supplier in enumerate(net.suppliers_echelon)
                for t, raw_material in enumerate(supplier.raw_materials)
            )
            constrain = wx_sum <= plant.capacity.sum()
            constrains.append(constrain)
            """(9) constrain"""
            constrain = wx_sum == lpSum(
                Y[i, j, p] for j, warehouse in enumerate(net.warehouses_echelon)
            )
            constrains.append(constrain)

        for j, warehouse in enumerate(net.warehouses_echelon):
            """(7) constrain"""
            y_sum = lpSum(
                Y[i, j, p]
                for p, product_capacity in enumerate(plant.product_capacity)
                for i, plant in enumerate(net.plants_echelon)
            )
            constrain = y_sum <= warehouse.capacity.sum()
            constrains.append(constrain)

        for k, dist_center in enumerate(net.distribution_centers_echelon):
            """(8) constrain"""
            z_sum = lpSum(
                Z[j, k, p]
                for p, product_capacity in enumerate(warehouse.product_capacity)
                for j, warehouse in enumerate(net.warehouses_echelon)
            )
            constrain = z_sum <= dist_center.capacity.sum()
            constrains.append(constrain)

        for j, warehouse in enumerate(net.warehouses_echelon):
            for p, product_capacity in enumerate(warehouse.product_capacity):
                """(10) constrain"""
                y_sum = lpSum(Y[i, j, p] for i, plant in enumerate(net.plants_echelon))
                z_sum = lpSum(
                    Z[j, k, p]
                    for k, dist_center in enumerate(net.distribution_centers_echelon)
                )
                constrain = y_sum == z_sum
                constrains.append(constrain)

        for k, distribution_center in enumerate(net.distribution_centers_echelon):
            for p, product_capacity in enumerate(distribution_center.product_capacity):
                """(11) constrain"""
                z_sum = lpSum(
                    Z[j, k, p] for j, warehouse in enumerate(net.warehouses_echelon)
                )
                q_sum = lpSum(
                    Q[k, m, p] for m, market in enumerate(net.markets_echelon)
                )
                constrain = z_sum == q_sum
                constrains.append(constrain)

        return constrains

    @property
    def multi_objective_value(self):
        model = LpProblem(name="Supply-Chain-Network", sense=LpMaximize)
        # model += self.Z1 - self.Z2 - self.Z3
        model += self.Z1

        for constrain in self.constrains:
            model += constrain
        # status = model.solve(solver=GLPK(msg=True))
        status = model.solve(solver=CPLEX_PY(msg=False))
        if status == 1:
            return model.objective.value()
        return status
