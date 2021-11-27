from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np
from constants import *


@dataclass
class PlantFacility:  # plant i
    products_prod_cost: List  # CPip cost of producing product p at plant I;
    products_trans_cost: Dict  # CTijp transportation cost of product p per km between plant i and warehouse j;
    fixed_cost: float  # Ei fixed cost for opening plant i;
    product_capacity: List  # Cip capacity of plant i for product p;
    warehouses_distances: List  # Tij the distance between plant at location i and warehouse at location j
    opening_env_impact: float  # EFi environmental impact of openingplant at location i;
    products_env_impact: List  # EPi environmental impact caused by production at plant i;
    products_trans_env_impact: Dict  # ETPijp environmental impact per unit and per distance caused by transporting product p from plant i to warehouse j;
    prop_delivery_risk: List  # Prdip probability of delivery risk for product p from plant i;
    prop_quality_risk: List  # Prqip probability of quality risk for product p produced at plant i;
    delivery_risk_impact: List  # IRDip impact caused by risk of delivery for product p from plant i;
    quality_risk_impact: List  # IRQip impact caused by risk of poor quality for product p from plant i;
    is_open: int = field(default=0)

    @property
    def capacity(self):
        return self.product_capacity

    @property
    def transportation_cost(self):
        return sum(
            products_costs.sum() for products_costs in self.products_trans_cost.values()
        )

    @classmethod
    def get_random_echelon(cls):
        howmany = NUMBER_OF_PLANTS
        number_of_products = NUMBER_OF_PRODUCTS
        number_of_warehouses = NUMBER_OF_WAREHOUSES
        random_products_prod_cost = (
            25 * np.random.rand(howmany, number_of_products) + 20
        )
        random_products_trans_cost = (
            0.18 * np.random.rand(howmany, number_of_warehouses, number_of_products)
            + 1.1
        )
        random_fixed_cost = 700_000 * np.random.rand(howmany) + 400_000
        random_product_capacity = (
            20_000 * np.random.rand(howmany, number_of_products) + 75_000
        )
        random_warehouses_distances = 3.38 * (
            np.random.rand(howmany, number_of_warehouses) + 0.18
        )
        random_opening_env_impact = 100_000_000_000 * (1 / random_fixed_cost) + 20000
        random_products_env_impact = 7 * np.random.rand(howmany, number_of_products) + 2
        random_products_trans_env_impact = (
            0.75 * np.random.rand(howmany, number_of_warehouses, number_of_products) + 2
        )
        random_prop_delivery_risk = (
            0.6 * np.random.rand(howmany, number_of_products) + 0.1
        )
        random_prop_quality_risk = (
            0.5 * np.random.rand(howmany, number_of_products) + 0.1
        )
        random_delivery_risk_impact = (
            70000 * np.random.rand(howmany, number_of_products) + 40000
        )
        random_quality_risk_impact = (
            50000 * np.random.rand(howmany, number_of_products) + 100000
        )
        facilities = list()
        for i in range(howmany):
            facility = cls(
                products_prod_cost=random_products_prod_cost[i],
                products_trans_cost={
                    warehouse_index: products_trans_costs
                    for warehouse_index, products_trans_costs in enumerate(
                        random_products_trans_cost[i]
                    )
                },
                fixed_cost=random_fixed_cost[i],
                product_capacity=random_product_capacity[i],
                warehouses_distances=random_warehouses_distances[i],
                opening_env_impact=random_opening_env_impact[i],
                products_env_impact=random_products_env_impact[i],
                products_trans_env_impact={
                    warehouse_index: products_impact
                    for warehouse_index, products_impact in enumerate(
                        random_products_trans_env_impact[i]
                    )
                },
                prop_delivery_risk=random_prop_delivery_risk[i],
                prop_quality_risk=random_prop_quality_risk[i],
                delivery_risk_impact=random_delivery_risk_impact[i],
                quality_risk_impact=random_quality_risk_impact[i],
            )
            facilities.append(facility)
        return facilities
