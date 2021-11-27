from dataclasses import dataclass
from typing import List

import numpy as np
from constants import *


@dataclass
class MarketFacility:  # Market M
    products_demand: List  # demand of customer m for product p

    @classmethod
    def get_random_echelon(cls):
        howmany = NUMBER_OF_MARKETS
        number_of_products = NUMBER_OF_PRODUCTS
        random_products_demand = 600 * np.random.rand(howmany, number_of_products) + 800
        facilities = list()
        for i in range(howmany):
            facility = cls(
                products_demand=random_products_demand[i],
            )
            facilities.append(facility)
        return facilities
