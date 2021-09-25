from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np


@dataclass
class Product:  # product p
    customer_demands: List  # Dmp demand of customers 1..m;

    @classmethod
    def get_random_products(cls, howmany=5, number_of_customers=5):
        products = list()
        random_demands = np.random.randint(1000, size=(howmany, number_of_customers))
        products = [cls(customer_demands=random_demands[i]) for i in range(howmany)]
        return products


@dataclass
class RawMaterial:  # raw material t
    products_yields: List  # Wtp yields of product 1..p;

    @classmethod
    def get_random_materials(cls, howmany=5, number_of_products=5):
        random_yields = 1000 * np.random.rand(
            howmany, number_of_products
        )  # random values between 0 and 1000
        materials = [cls(products_yields=random_yields[i]) for i in range(howmany)]
        return materials


@dataclass
class SuppliersEchelon:  # supplier object s
    raw_materials: List[RawMaterial]
    material_purchase_cost: List  # CCst purchase cost of raw material t from supplier s;
    material_trans_cost: List  # CBsit transportation cost of raw material t per km between supplier s and plant i ;
    material_capacity: List  # Cst capacity of supplier s for raw material t;
    plants_distances: List  # Tsi the distance between supplier s and plant at location i
    material_trans_env_impact: List  # ETSsit environmental impact per unit and per distance caused by transporting raw material t from supplier s to plant i;
    prop_delivery_risk: List  # Prdst probability of delivery risk for raw material t from supplier s;
    prop_quality_risk: List  # Prqst probability of quality risk for raw material t from supplier s;
    delivery_risk_impact: List  # IRDst impact caused by risk of delivery for raw material t from supplier s;
    quality_risk_impact: List  # IRQst impact caused by risk of quality for raw material t from supplier s;
    is_open: bool = field(default=False)

    @classmethod
    def get_random_echelon(cls):
        pass


@dataclass
class PlantsEchelon:
    products_prod_cost: Dict  # CPip cost of producing product p at plant I;
    products_trans_cost: Dict  # CTijp transportation cost of product p per km between plant i and warehouse j;
    fixed_cost: float  # Ei fixed cost for opening plant i;
    product_capacity: Dict  # Cip capacity of plant i for product p;
    distances: Dict  # Tij the distance between plant at location i and warehouse at location j
    opening_env_impact: float  # EFi environmental impact of openingplant at location i;
    production_env_impact: float  # EPi environmental impact caused by production at plant i;
    product_trans_env_impact: Dict  # ETPijp environmental impact per unit and per distance caused by transporting product p from plant i to warehouse j;
    prop_delivery_risk: Dict  # Prdip probability of delivery risk for product p from plant i;
    prop_quality_risk: Dict  # Prqip probability of quality risk for product p produced at plant i;
    delivery_risk_impact: Dict  # IRDip impact caused by risk of delivery for product p from plant i;
    quality_risk_impact: Dict  # IRQip impact caused by risk of poor quality for product p from plant i;
    is_open: bool = field(default=False)


@dataclass
class WarehouseEchelon:
    products_trans_cost: Dict  # CDjkp transportation cost of product p per km between warehouse j and distribution center k;
    fixed_cost: float  # Fj fixed cost for opening warehouse j;
    product_capacity: Dict  # Cjp capacity of warehouse j for product p;
    distances: Dict  # Tjk the distance between warehouse at location j and distribution center at location k
    opening_env_impact: float  # EWj environmental impact of opening warehouse center at location j;
    product_trans_env_impact: Dict  # ETDjkp environmental impact per unit and per distance caused by transporting product p from warehouse j to distribution center k;
    prop_delivery_risk: Dict  # Prdjp probability of delivery risk for product p from warehouse j;
    delivery_risk_impact: Dict  # IRDjp impact caused by risk of delivery for product p from warehouse j;
    is_open: bool = field(default=False)


@dataclass
class DistributionCenter:
    products_trans_cost: Dict
    fixed_cost: float  # Gk fixed cost for opening distribution center k;
    product_capacity: Dict  # Ckp capacity of distribution center k for product p;
    distances: Dict  # tkm the distance between distribution center at location k and market m
    opening_env_impact: float  # EDk environmental impact of opening distribution center at location k;
    product_trans_env_impact: Dict  # ETWkmp environmental impact per unit and per distance caused by transporting product p from distribution center k to market m;
    selling_prices: Dict  # SPkmp selling price of product p transported from distribution centerk at market m;
    prop_delivery_risk: Dict  # Prdkp probability of delivery risk for product p from distribution center k;
    delivery_risk_impact: Dict  # IRDkp impactcaused by risk of delivery for product p from distribution center k.
    is_open: bool = field(default=False)
