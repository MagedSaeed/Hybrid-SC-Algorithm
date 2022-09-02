from dataclasses import dataclass, field
from typing import List

import numpy as np
from .base_facility import BaseFacility


@dataclass
class RawMaterial(BaseFacility):  # raw material t
    products_yields: List  # Wtp yields of product 1..p;

    @classmethod
    def get_random_materials(cls):
        cls._configure()
        howmany = cls.NUMBER_OF_RAW_MATERIALS
        number_of_products = cls.NUMBER_OF_PRODUCTS
        """
        by assumption, raw material should equal to 
        products.
        by default, each raw material item will generate one product item,
        the rest will generate zero products items
        """
        assert (
            howmany == number_of_products
        ), "number of raw material should be equal to number of products"
        random_yields = np.identity(number_of_products)
        # random_yields = np.ones((howmany, number_of_products))
        # random_yields = 1000 * np.random.rand(
        # howmany, number_of_products
        # )  # random values between 0 and 1000# random values between 0 and 1000
        materials = [cls(products_yields=random_yields[i]) for i in range(howmany)]
        return materials
