from dataclasses import dataclass
from typing import List

import numpy as np
from .base_facility import BaseFacility


@dataclass
class MarketFacility(BaseFacility):  # Market M
    products_demand: List  # demand of customer m for product p

    @classmethod
    def get_random_echelon(cls):
        cls._configure()
        howmany = cls.NUMBER_OF_MARKETS
        number_of_products = cls.NUMBER_OF_PRODUCTS
        random_products_demand = (
            6000 * np.random.rand(howmany, number_of_products) + 8000
        )
        facilities = list()
        for i in range(howmany):
            facility = cls(
                products_demand=random_products_demand[i],
            )
            facilities.append(facility)
        return facilities
