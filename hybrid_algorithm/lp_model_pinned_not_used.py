from functools import cached_property
import itertools
from hybrid_algorithm.utils import exclude_closed_facilities, get_three_random_weights

from pulp import CPLEX_PY, GLPK, LpMaximize, LpMinimize, LpProblem, LpVariable, lpSum

from hybrid_algorithm.config import AppConfig
from hybrid_algorithm.utils import exclude_closed_facilities, get_three_random_weights


class LPModel:
    def __init__(self, network):
        self.network = exclude_closed_facilities(network, inplace=False)
        # self.network = network

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
    def Z1_objective_function(self):
        net = self.network
        EX = sum(
            facility.fixed_cost * facility.is_open
            for facility in self.network.plants_echelon
        )
        FY = sum(
            facility.fixed_cost * facility.is_open
            for facility in self.network.warehouses_echelon
        )
        GZ = sum(
            facility.fixed_cost * facility.is_open
            for facility in self.network.distribution_centers_echelon
        )

        # Xsit_coeffs = [
        #     [
        #         [
        #             (
        #                 material_cost
        #                 + supplier.plants_distances[plant_index] * material_trans_cost
        #             )
        #             for material_trans_cost in supplier.material_trans_cost[plant_index]
        #         ]
        #         for plant_index, material_cost in zip(
        #             supplier.material_trans_cost.keys(),
        #             supplier.material_purchase_cost,
        #         )
        #     ]
        #     for supplier in net.suppliers_echelon
        # ]

        # Xsit_sum = lpSum(
        #     coeff * self.Xsit[(s, i, t)]
        #     for s, supplier in enumerate(Xsit_coeffs)
        #     for i, plant in enumerate(Xsit_coeffs[s])
        #     for t, coeff in enumerate(Xsit_coeffs[s][i])
        # )

        Xsit_coeffs = list()
        for supplier in net.suppliers_echelon:
            for (
                plant_index,
                material_trans_costs,
            ) in supplier.material_trans_cost.items():
                for material_index, material_purchase_cost in enumerate(
                    supplier.material_purchase_cost
                ):
                    coeff = (
                        material_purchase_cost
                        + material_trans_costs[material_index]
                        * supplier.plants_distances[plant_index]
                    )
                    Xsit_coeffs.append(coeff)

        number_of_materials = len(net.suppliers_echelon[0].material_purchase_cost)
        assert len(self.Xsit) == len(Xsit_coeffs)
        Xsit_sum = lpSum(
            coeff * self.Xsit[(s, i, t)]
            for coeff, (s, i, t) in zip(
                Xsit_coeffs,
                itertools.product(
                    range(len(net.suppliers_echelon)),
                    range(len(net.plants_echelon)),
                    range(number_of_materials),
                ),
            )
        )

        # Yijp_coeffs = [
        #     [
        #         [
        #             (
        #                 production_cost
        #                 + plant.warehouses_distances[warehouse_index]
        #                 * product_trans_cost
        #             )
        #             for product_trans_cost in plant.products_trans_cost[warehouse_index]
        #         ]
        #         for warehouse_index, production_cost in zip(
        #             plant.products_trans_cost.keys(),
        #             plant.products_prod_cost,
        #         )
        #     ]
        #     for plant in net.plants_echelon
        # ]

        # Yijp_sum = lpSum(
        #     coeff * self.Yijp[(i, j, p)]
        #     for i, plant in enumerate(Yijp_coeffs)
        #     for j, warehouse in enumerate(Yijp_coeffs[i])
        #     for p, coeff in enumerate(Yijp_coeffs[i][j])
        # )

        Yijp_coeffs = list()
        for plant in net.plants_echelon:
            for (
                warehouse_index,
                products_trans_costs,
            ) in plant.products_trans_cost.items():
                for product_index, product_production_cost in enumerate(
                    plant.products_prod_cost
                ):
                    coeff = (
                        product_production_cost
                        + products_trans_costs[product_index]
                        * plant.warehouses_distances[warehouse_index]
                    )
                    Yijp_coeffs.append(coeff)
        number_of_products = len(net.plants_echelon[0].products_prod_cost)
        assert len(Yijp_coeffs) == len(self.Yijp)
        Yijp_sum = lpSum(
            coeff * self.Yijp[(i, j, p)]
            for coeff, (i, j, p) in zip(
                Yijp_coeffs,
                itertools.product(
                    range(len(net.plants_echelon)),
                    range(len(net.warehouses_echelon)),
                    range(number_of_products),
                ),
            )
        )
        Zjkp_coeffs = list()
        for warehouse in net.warehouses_echelon:
            for (
                dist_center_index,
                products_trans_costs,
            ) in warehouse.products_trans_cost.items():
                for product_t_cost in products_trans_costs:
                    coeff = (
                        product_t_cost
                        * warehouse.dist_centers_distances[dist_center_index]
                    )
                    Zjkp_coeffs.append(coeff)
        assert len(self.Zjkp) == len(Zjkp_coeffs)
        Zjkp_sum = lpSum(
            coeff * self.Zjkp[(j, k, p)]
            for coeff, (j, k, p) in zip(
                Zjkp_coeffs,
                itertools.product(
                    range(len(net.warehouses_echelon)),
                    range(len(net.distribution_centers_echelon)),
                    range(number_of_products),
                ),
            )
        )

        # Zjkp_coeffs = [
        #     [
        #         [
        #             warehouse.dist_centers_distances[dist_center_index]
        #             * product_trans_cost
        #             for product_trans_cost in warehouse.products_trans_cost[
        #                 dist_center_index
        #             ]
        #         ]
        #         for dist_center_index in warehouse.products_trans_cost.keys()
        #     ]
        #     for warehouse in net.warehouses_echelon
        # ]

        # Zjkp_sum = lpSum(
        #     coeff * self.Zjkp[(j, k, p)]
        #     for j, warehouse in enumerate(Zjkp_coeffs)
        #     for k, dist_center in enumerate(Zjkp_coeffs[j])
        #     for p, coeff in enumerate(Zjkp_coeffs[j][k])
        # )

        Qkmp_coeffs = list()
        for dist_center in net.distribution_centers_echelon:
            for (
                market_index,
                products_trans_costs,
            ) in dist_center.products_trans_cost.items():
                for product_index, product_price in enumerate(
                    dist_center.selling_prices[market_index]
                ):
                    # print(product_price)
                    coeff = (
                        product_price
                        - dist_center.market_distances[market_index]
                        * products_trans_costs[product_index]
                    )
                    Qkmp_coeffs.append(coeff)
        assert len(self.Qkmp) == len(Qkmp_coeffs)
        Qkmp_sum = lpSum(
            coeff * self.Qkmp[(k, m, p)]
            for coeff, (k, m, p) in zip(
                Qkmp_coeffs,
                itertools.product(
                    range(len(net.distribution_centers_echelon)),
                    range(len(net.markets_echelon)),
                    range(number_of_products),
                ),
            )
        )

        # Qkmp_coeffs = [
        #     [
        #         [
        #             (
        #                 product_price
        #                 - dist_center.market_distances[market_index]
        #                 * product_trans_cost
        #             )
        #             for product_trans_cost, product_price in zip(
        #                 dist_center.products_trans_cost[market_index],
        #                 dist_center.selling_prices[market_index],
        #             )
        #         ]
        #         for market_index in dist_center.products_trans_cost.keys()
        #     ]
        #     for dist_center in net.distribution_centers_echelon
        # ]

        # Qkmp_sum = lpSum(
        #     coeff * self.Qkmp[(k, m, p)]
        #     for k, dist_center in enumerate(Qkmp_coeffs)
        #     for m, market in enumerate(Qkmp_coeffs[k])
        #     for p, coeff in enumerate(Qkmp_coeffs[k][m])
        # )

        return Qkmp_sum - (EX + FY + GZ + Xsit_sum + Yijp_sum + Zjkp_sum)

    @property
    def Z2_objective_value(self):
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
        assert len(U_coeffs), len(net.suppliers_echelon)
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
        assert len(X_coeffs) == len(net.plants_echelon)
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
        assert len(Y_coeffs) == len(net.warehouses_echelon)
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
        assert len(Z_coeffs) == len(net.distribution_centers_echelon)
        Z = sum(
            Zk.is_open * Z_coeff
            for Z_coeff, Zk in zip(Z_coeffs, net.distribution_centers_echelon)
        )
        return U + X + Y + Z

    @property
    def Z3_objective_function(self):
        net = self.network
        EFX = sum(X.opening_env_impact * X.is_open for X in net.plants_echelon)
        EWY = sum(Y.opening_env_impact * Y.is_open for Y in net.warehouses_echelon)
        EDZ = sum(
            Z.opening_env_impact * Z.is_open for Z in net.distribution_centers_echelon
        )
        EPY = sum(Y.products_env_impact.sum() * Y.is_open for Y in net.plants_echelon)

        Xsit_coeffs = [
            [
                [
                    supplier.is_open * material_impact * plant_distance
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

        Yijp_coeffs = list()
        for plant in self.network.plants_echelon:
            for warehouse_index, warehouse_distance in enumerate(
                plant.warehouses_distances
            ):
                for product_index, product_env_impact in enumerate(
                    plant.products_env_impact
                ):
                    coeff = plant.is_open * (
                        product_env_impact
                        + plant.products_trans_env_impact[warehouse_index][
                            product_index
                        ]
                        * warehouse_distance
                    )
                    Yijp_coeffs.append(coeff)
        number_of_products = len(net.plants_echelon[0].products_prod_cost)
        Yijp_sum = lpSum(
            coeff * self.Yijp[(i, j, p)]
            for coeff, (i, j, p) in zip(
                Yijp_coeffs,
                itertools.product(
                    range(len(net.plants_echelon)),
                    range(len(net.warehouses_echelon)),
                    range(number_of_products),
                ),
            )
        )

        # Yijp_coeffs = [
        #     [
        #         [
        #             product_env_impact + product_trans_impact * warehouse_distance
        #             for product_trans_impact, product_env_impact in zip(
        #                 plant.products_trans_env_impact[warehouse_index],
        #                 plant.products_env_impact,
        #             )
        #         ]
        #         for warehouse_index, warehouse_distance in enumerate(
        #             plant.warehouses_distances
        #         )
        #     ]
        #     for plant in self.network.plants_echelon
        # ]

        # Yijp_sum = lpSum(
        #     coeff * self.Yijp[(i, j, p)]
        #     for i, plant in enumerate(Yijp_coeffs)
        #     for j, warehouse in enumerate(Yijp_coeffs[i])
        #     for p, coeff in enumerate(Yijp_coeffs[i][j])
        # )

        Zjkp_coeffs = [
            [
                [
                    warehouse.is_open * product_impact * dist_center_distance
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
                    dist_center.is_open * product_impact * market_distance
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
        return EFX + EWY + EDZ + EPY + Yijp_sum + Xsit_sum + Zjkp_sum + Qkmp_sum

    @cached_property
    def constraints(self):
        net = self.network
        constraints = list()

        Q = self.Qkmp
        X = self.Xsit
        Y = self.Yijp
        Z = self.Zjkp

        for m, market in enumerate(net.markets_echelon):
            for p, demand in enumerate(market.products_demand):
                """(4) constrain"""
                constraint = (
                    lpSum(
                        Q[k, m, p]
                        for k, dist_center in enumerate(
                            net.distribution_centers_echelon
                        )
                    )
                    == demand
                )
                constraints.append(constraint)

        for s, supplier in enumerate(net.suppliers_echelon):
            """(5) constrain"""
            # for t, capacity in enumerate(supplier.material_capacity):
            constraint = (
                lpSum(
                    X[s, i, t]
                    for i, plant in enumerate(net.plants_echelon)
                    for t, capacity in enumerate(supplier.material_capacity)
                )
                <= supplier.capacity.sum() * supplier.is_open
            )
            constraints.append(constraint)

        for i, plant in enumerate(net.plants_echelon):
            """(6) constrain"""
            # for p, capacity in enumerate(plant.product_capacity):
            """
            The implementation should include the products yields. However, the yields are 1. So, we neglect them.
            """
            wx_sum = lpSum(
                X[s, i, p]
                for s, supplier in enumerate(net.suppliers_echelon)
                # for t, raw_material in enumerate(supplier.raw_materials)
                for p, capacity in enumerate(plant.product_capacity)
            )
            constraint = wx_sum <= plant.capacity.sum() * plant.is_open
            constraints.append(constraint)

        for j, warehouse in enumerate(net.warehouses_echelon):
            """(7) constrain"""
            y_sum = lpSum(
                Y[i, j, p]
                for i, plant in enumerate(net.plants_echelon)
                for p, product_capacity in enumerate(plant.product_capacity)
            )
            constraint = y_sum <= warehouse.capacity.sum() * warehouse.is_open
            constraints.append(constraint)

        for k, dist_center in enumerate(net.distribution_centers_echelon):
            """(8) constrain"""
            z_sum = lpSum(
                Z[j, k, p]
                for j, warehouse in enumerate(net.warehouses_echelon)
                for p, product_capacity in enumerate(warehouse.product_capacity)
            )
            constraint = z_sum <= dist_center.capacity.sum() * dist_center.is_open
            constraints.append(constraint)

        for i, plant in enumerate(net.plants_echelon):
            """(9) constrain"""
            for p, capacity in enumerate(plant.product_capacity):
                """
                The implementation should include the products yields. However, the yields are 1. So, we neglect them.
                """
                wx_sum = lpSum(
                    X[s, i, p]
                    for s, supplier in enumerate(net.suppliers_echelon)
                    # for t, raw_material in enumerate(supplier.raw_materials)
                    # for p, capacity in enumerate(plant.product_capacity)
                )
                constraint = wx_sum == lpSum(
                    Y[i, j, p]
                    for j, warehouse in enumerate(net.warehouses_echelon)
                    # for p, capacity in enumerate(plant.product_capacity)
                )
                constraints.append(constraint)

        for j, warehouse in enumerate(net.warehouses_echelon):
            for p, product_capacity in enumerate(warehouse.product_capacity):
                """(10) constrain"""
                y_sum = lpSum(Y[i, j, p] for i, plant in enumerate(net.plants_echelon))
                z_sum = lpSum(
                    Z[j, k, p]
                    for k, dist_center in enumerate(net.distribution_centers_echelon)
                )
                constraint = y_sum == z_sum
                constraints.append(constraint)

        for k, distribution_center in enumerate(net.distribution_centers_echelon):
            for p, product_capacity in enumerate(distribution_center.product_capacity):
                """(11) constrain"""
                z_sum = lpSum(
                    Z[j, k, p] for j, warehouse in enumerate(net.warehouses_echelon)
                )
                q_sum = lpSum(
                    Q[k, m, p] for m, market in enumerate(net.markets_echelon)
                )
                constraint = z_sum == q_sum
                constraints.append(constraint)
        return constraints

    def _get_objective_value(self, objective_function):
        model = LpProblem(name="Supply-Chain-Network", sense=LpMinimize)
        model += objective_function
        for constraint in self.constraints:
            model += constraint
        # status = model.solve(solver=GLPK(msg=False))
        status = model.solve(solver=CPLEX_PY(msg=False))
        if status == 1:
            return model.objective.value()
        return None

    def _get_normalized_objective_value(
        self,
        objective_value,
        max_value,
        min_value,
        sense=LpMinimize,
    ):
        if objective_value is None:
            return None
        if sense == LpMaximize:
            numerator = max_value - abs(objective_value)
        elif sense == LpMinimize:
            numerator = abs(objective_value) - min_value
        denumerator = max_value - min_value
        return numerator / denumerator

    @cached_property
    def Z1_objective_value(self):
        return self._get_objective_value(objective_function=-self.Z1_objective_function)

    @cached_property
    def Z3_objective_value(self):
        return self._get_objective_value(objective_function=self.Z3_objective_function)

    @cached_property
    def multi_objective_value(self):
        return self._get_objective_value(
            objective_function=-self.Z1_objective_function
            + self.Z2_objective_value
            + self.Z3_objective_function
        )

    @cached_property
    def Z1_normalized_objective_value(self):
        max_value = int(AppConfig.config["lp_model"]["z1_max"])
        min_value = int(AppConfig.config["lp_model"]["z1_min"])
        return self._get_normalized_objective_value(
            objective_value=self.Z1_objective_value,
            max_value=max_value,
            min_value=min_value,
            sense=LpMaximize,
        )

    @cached_property
    def Z2_normalized_objective_value(self):
        max_value = int(AppConfig.config["lp_model"]["z2_max"])
        min_value = int(AppConfig.config["lp_model"]["z2_min"])
        return self._get_normalized_objective_value(
            objective_value=self.Z2_objective_value,
            max_value=max_value,
            min_value=min_value,
        )

    @cached_property
    def Z3_normalized_objective_value(self):
        max_value = int(AppConfig.config["lp_model"]["z3_max"])
        min_value = int(AppConfig.config["lp_model"]["z3_min"])
        return self._get_normalized_objective_value(
            objective_value=self.Z3_objective_value,
            max_value=max_value,
            min_value=min_value,
        )

    @cached_property
    def normalized_multi_objective_value(self):
        max_value = int(AppConfig.config["lp_model"]["multi_max"])
        min_value = int(AppConfig.config["lp_model"]["multi_min"])
        return self._get_normalized_objective_value(
            objective_value=self.multi_objective_value,
            max_value=max_value,
            min_value=min_value,
        )

    @cached_property
    def weighted_multi_objective_value(self):
        w1, w2, w3 = (
            float(AppConfig.config["lp_model"]["z1_weight"]),
            float(AppConfig.config["lp_model"]["z2_weight"]),
            float(AppConfig.config["lp_model"]["z3_weight"]),
        )
        if not all(
            [
                self.Z1_normalized_objective_value,
                self.Z2_normalized_objective_value,
                self.Z3_normalized_objective_value,
            ]
        ):
            return None
        weighted_objective_value = (
            w1 * self.Z1_normalized_objective_value
            + w2 * self.Z2_normalized_objective_value
            + w3 * self.Z3_normalized_objective_value
        )

        return weighted_objective_value
