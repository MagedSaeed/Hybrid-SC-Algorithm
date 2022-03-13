from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np

from hybrid_algorithm.facilities.base_facility import BaseFacility


@dataclass
class WarehouseFacility(BaseFacility):  # warehouse j
    products_trans_cost: List  # CDjkp transportation cost of product p per km between warehouse j and distribution center k;
    fixed_cost: float  # Fj fixed cost for opening warehouse j;
    product_capacity: List  # Cjp capacity of warehouse j for product p;
    dist_centers_distances: List  # Tjk the distance between warehouse at location j and distribution center at location k
    opening_env_impact: float  # EWj environmental impact of opening warehouse center at location j;
    products_trans_env_impact: Dict  # ETDjkp environmental impact per unit and per distance caused by transporting product p from warehouse j to distribution center k;
    prop_delivery_risk: List  # Prdjp probability of delivery risk for product p from warehouse j;
    delivery_risk_impact: List  # IRDjp impact caused by risk of delivery for product p from warehouse j;
    is_open: int = field(default=0)

    @property
    def transportation_cost(self):
        return sum(
            products_costs.sum() for products_costs in self.products_trans_cost.values()
        )

    @property
    def capacity(self):
        return self.product_capacity

    @classmethod
    def get_random_echelon(cls):
        cls._configure()
        howmany = cls.NUMBER_OF_WAREHOUSES
        number_of_products = cls.NUMBER_OF_PRODUCTS
        number_of_dist_centers = cls.NUMBER_OF_DISTRIBUTION_CENTERS
        random_products_trans_cost = (
            0.18 * np.random.rand(howmany, number_of_dist_centers, number_of_products)
            + 1.1
        )
        random_fixed_cost = 30_000 * np.random.rand(howmany) + 40_000
        random_product_capacity = (
            15_000 * np.random.rand(howmany, number_of_products) + 75_000
        )
        random_dist_centers_distances = (
            3.38 * np.random.rand(howmany, number_of_dist_centers) + 0.18
        )
        random_opening_env_impact = 100_000_000_000 * (1 / random_fixed_cost) + 20000
        random_products_trans_env_impact = (
            0.5 * np.random.rand(howmany, number_of_dist_centers, number_of_products)
            + 2
        )
        random_prop_delivery_risk = (
            0.4 * np.random.rand(howmany, number_of_products) + 0.1
        )
        random_delivery_risk_impact = (
            40000 * np.random.rand(howmany, number_of_products) + 20000
        )
        facilities = list()
        for i in range(howmany):
            facility = cls(
                products_trans_cost={
                    dist_center_index: products_trans_costs
                    for dist_center_index, products_trans_costs in enumerate(
                        random_products_trans_cost[i]
                    )
                },
                fixed_cost=random_fixed_cost[i],
                product_capacity=random_product_capacity[i],
                dist_centers_distances=random_dist_centers_distances[i],
                opening_env_impact=random_opening_env_impact[i],
                products_trans_env_impact={
                    dist_center_index: products_impact
                    for dist_center_index, products_impact in enumerate(
                        random_products_trans_env_impact[i]
                    )
                },
                prop_delivery_risk=random_prop_delivery_risk[i],
                delivery_risk_impact=random_delivery_risk_impact[i],
            )
            facilities.append(facility)
        return facilities
