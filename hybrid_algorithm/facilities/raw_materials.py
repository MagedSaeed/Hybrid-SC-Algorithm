from dataclasses import dataclass, field
from typing import List

import numpy as np

from hybrid_algorithm.facilities.base_facility import BaseFacility


@dataclass
class RawMaterial(BaseFacility):  # raw material t
    products_yields: List  # Wtp yields of product 1..p;

    @classmethod
    def get_random_materials(cls):
        cls._configure()
        howmany = cls.NUMBER_OF_RAW_MATERIALS
        number_of_products = cls.NUMBER_OF_PRODUCTS
        random_yields = np.ones((howmany, number_of_products))
        # random_yields = 1000 * np.random.rand(
        # howmany, number_of_products
        # )  # random values between 0 and 1000# random values between 0 and 1000
        materials = [cls(products_yields=random_yields[i]) for i in range(howmany)]
        return materials
