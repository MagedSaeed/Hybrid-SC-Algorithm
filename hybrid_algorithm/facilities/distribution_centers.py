from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np
from constants import *


@dataclass
class DistributionCenterFacility:  # center k
    products_trans_cost: Dict  # COkmp transportation cost of product p per km between distribution center k and demand market m ;
    fixed_cost: float  # Gk fixed cost for opening distribution center k;
    product_capacity: List  # Ckp capacity of distribution center k for product p;
    market_distances: List  # tkm the distance between distribution center at location k and market m
    opening_env_impact: float  # EDk environmental impact of opening distribution center at location k;
    products_trans_env_impact: Dict  # ETWkmp environmental impact per unit and per distance caused by transporting product p from distribution center k to market m;
    selling_prices: Dict  # SPkmp selling price of product p transported from distribution center k at market m;
    prop_delivery_risk: List  # Prdkp probability of delivery risk for product p from distribution center k;
    delivery_risk_impact: List  # IRDkp impactcaused by risk of delivery for product p from distribution center k.
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
        howmany = NUMBER_OF_DISTRIBUTION_CENTERS
        number_of_products = NUMBER_OF_PRODUCTS
        number_of_markets = NUMBER_OF_MARKETS
        random_products_trans_cost = (
            0.18 * np.random.rand(howmany, number_of_markets, number_of_products) + 1.3
        )
        random_fixed_cost = 40_000 * np.random.rand(howmany) + 40_000
        random_product_capacity = (
            10_000 * np.random.rand(howmany, number_of_products) + 80_000
        )
        random_market_distances_distances = (
            7.31 * np.random.rand(howmany, number_of_markets) + 0.18
        )
        random_opening_env_impact = 100_000_000_000 * (1 / random_fixed_cost) + 20000
        random_products_trans_env_impact = (
            1.5 * np.random.rand(howmany, number_of_markets, number_of_products) + 1.5
        )
        random_selling_prices = (
            100 * np.random.rand(howmany, number_of_markets, number_of_products) + 2000
        )
        random_prop_delivery_risk = (
            0.5 * np.random.rand(howmany, number_of_products) + 0.1
        )
        random_delivery_risk_impact = (
            50_000 * np.random.rand(howmany, number_of_products) + 30_000
        )
        facilities = list()
        for i in range(howmany):
            facility = cls(
                products_trans_cost={
                    market_index: products_trans_costs
                    for market_index, products_trans_costs in enumerate(
                        random_products_trans_cost[i]
                    )
                },
                fixed_cost=random_fixed_cost[i],
                product_capacity=random_product_capacity[i],
                market_distances=random_market_distances_distances[i],
                opening_env_impact=random_opening_env_impact[i],
                products_trans_env_impact={
                    market_index: products_impact
                    for market_index, products_impact in enumerate(
                        random_products_trans_env_impact[i]
                    )
                },
                selling_prices={
                    market_index: product_prices
                    for market_index, product_prices in enumerate(
                        random_selling_prices[i]
                    )
                },
                prop_delivery_risk=random_prop_delivery_risk[i],
                delivery_risk_impact=random_delivery_risk_impact[i],
            )
            facilities.append(facility)
        return facilities
