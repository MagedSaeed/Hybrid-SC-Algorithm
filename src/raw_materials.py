from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np

from constants import *


@dataclass
class RawMaterial:  # raw material t
    products_yields: List  # Wtp yields of product 1..p;

    @classmethod
    def get_random_materials(cls):
        howmany = NUMBER_OF_RAW_MATERIALS
        number_of_products = NUMBER_OF_PRODUCTS
        random_yields = np.ones((howmany, number_of_products))
        # random_yields = 1000 * np.random.rand(
        # howmany, number_of_products
        # )  # random values between 0 and 1000# random values between 0 and 1000
        materials = [cls(products_yields=random_yields[i]) for i in range(howmany)]
        return materials
