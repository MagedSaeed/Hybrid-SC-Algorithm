from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np
from beautifultable import BeautifulTable


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
class SupplierFacility:  # supplier object s
    raw_materials: List[RawMaterial]
    material_purchase_cost: List  # CCst purchase cost of raw material t from supplier s;
    material_trans_cost: Dict  # CBsit transportation cost of raw material t per km between supplier s and plant i ;
    material_capacity: List  # Cst capacity of supplier s for raw material t;
    plants_distances: List  # Tsi the distance between supplier s and plant at location i
    material_trans_env_impact: Dict  # ETSsit environmental impact per unit and per distance caused by transporting raw material t from supplier s to plant i;
    prop_delivery_risk: List  # Prdst probability of delivery risk for raw material t from supplier s;
    prop_quality_risk: List  # Prqst probability of quality risk for raw material t from supplier s;
    delivery_risk_impact: List  # IRDst impact caused by risk of delivery for raw material t from supplier s;
    quality_risk_impact: List  # IRQst impact caused by risk of quality for raw material t from supplier s;
    fixed_cost: float
    is_open: int = field(default=1)

    @property
    def capacity(self):
        return self.material_capacity

    @property
    def transportation_cost(self):
        return sum(
            materials_costs.sum()
            for materials_costs in self.material_trans_cost.values()
        )

    @classmethod
    def get_random_echelon(cls, howmany=5, number_of_plants=5):
        raw_materials = RawMaterial.get_random_materials()
        random_material_purchase_cost = (
            np.random.rand(howmany, len(raw_materials)) * 1000
        )
        random_material_trans_cost = (
            np.random.rand(howmany, len(raw_materials), number_of_plants) * 1000
        )
        random_material_capacity = np.random.rand(howmany, len(raw_materials)) * 100
        random_plants_distances = np.random.rand(howmany, number_of_plants) * 100
        random_material_trans_env_impact = (
            np.random.rand(howmany, len(raw_materials), number_of_plants) * 100
        )
        random_prop_delivery_risk = np.random.rand(howmany, len(raw_materials))
        random_prop_quality_risk = np.random.rand(howmany, len(raw_materials))
        random_delivery_risk_impact = np.random.rand(howmany, len(raw_materials)) * 100
        random_quality_risk_impact = np.random.rand(howmany, len(raw_materials)) * 100
        random_fixed_costs = np.random.rand(howmany) * 1000
        facilities = list()
        for i in range(howmany):
            facility = cls(
                raw_materials=raw_materials,
                material_purchase_cost=random_material_purchase_cost[i],
                material_trans_cost={
                    material_index: plants_trans_costs
                    for material_index, plants_trans_costs in enumerate(
                        random_material_trans_cost[i]
                    )
                },
                material_capacity=random_material_capacity[i],
                plants_distances=random_plants_distances[i],
                material_trans_env_impact={
                    material_index: plant_impact
                    for material_index, plant_impact in enumerate(
                        random_material_trans_env_impact[i]
                    )
                },
                prop_delivery_risk=random_prop_delivery_risk[i],
                prop_quality_risk=random_prop_quality_risk[i],
                delivery_risk_impact=random_delivery_risk_impact[i],
                quality_risk_impact=random_quality_risk_impact[i],
                fixed_cost=random_fixed_costs[i],
            )
            facilities.append(facility)
        return facilities


@dataclass
class PlantFacility:  # plant i
    products_prod_cost: List  # CPip cost of producing product p at plant I;
    products_trans_cost: Dict  # CTijp transportation cost of product p per km between plant i and warehouse j;
    fixed_cost: float  # Ei fixed cost for opening plant i;
    product_capacity: List  # Cip capacity of plant i for product p;
    warehouse_distances: List  # Tij the distance between plant at location i and warehouse at location j
    opening_env_impact: float  # EFi environmental impact of openingplant at location i;
    production_env_impact: float  # EPi environmental impact caused by production at plant i;
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
    def get_random_echelon(
        cls, howmany=5, number_of_products=5, number_of_warehouses=5
    ):
        random_products_prod_cost = np.random.rand(howmany, number_of_products) * 100
        random_products_trans_cost = (
            np.random.rand(howmany, number_of_products, number_of_warehouses) * 100
        )
        random_fixed_cost = np.random.rand(howmany) * 1000
        random_product_capacity = np.random.rand(howmany, number_of_products) * 500
        random_warehouse_distances = np.random.rand(howmany, number_of_warehouses) * 100
        random_opening_env_impact = np.random.rand(howmany) * 1000
        random_production_env_impact = (
            np.random.rand(howmany, number_of_products, number_of_warehouses) * 100
        )
        random_products_trans_env_impact = (
            np.random.rand(howmany, number_of_products) * 1000
        )
        random_prop_delivery_risk = np.random.rand(howmany, number_of_products) * 1000
        random_prop_quality_risk = np.random.rand(howmany, number_of_products) * 1000
        random_delivery_risk_impact = np.random.rand(howmany, number_of_products) * 1000
        random_quality_risk_impact = np.random.rand(howmany, number_of_products) * 1000
        facilities = list()
        for i in range(howmany):
            facility = cls(
                products_prod_cost=random_products_prod_cost[i],
                products_trans_cost={
                    product_index: warehouse_trans_costs
                    for product_index, warehouse_trans_costs in enumerate(
                        random_products_trans_cost[i]
                    )
                },
                fixed_cost=random_fixed_cost[i],
                product_capacity=random_product_capacity[i],
                warehouse_distances=random_warehouse_distances[i],
                opening_env_impact=random_opening_env_impact[i],
                production_env_impact=random_production_env_impact[i],
                products_trans_env_impact={
                    product_index: warehouse_impact
                    for product_index, warehouse_impact in enumerate(
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


@dataclass
class WarehouseFacility:  # warehouse j
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
    def get_random_echelon(
        cls, howmany=5, number_of_products=5, number_of_dist_centers=5
    ):
        random_products_trans_cost = (
            np.random.rand(howmany, number_of_products, number_of_dist_centers) * 100
        )
        random_fixed_cost = np.random.rand(howmany) * 1000
        random_product_capacity = np.random.rand(howmany, number_of_products) * 500
        random_dist_centers_distances = (
            np.random.rand(howmany, number_of_dist_centers) * 100
        )
        random_opening_env_impact = np.random.rand(howmany) * 1000
        random_products_trans_env_impact = (
            np.random.rand(howmany, number_of_products) * 1000
        )
        random_prop_delivery_risk = np.random.rand(howmany, number_of_products) * 1000
        random_delivery_risk_impact = np.random.rand(howmany, number_of_products) * 1000
        facilities = list()
        for i in range(howmany):
            facility = cls(
                products_trans_cost={
                    product_index: dist_center_trans_costs
                    for product_index, dist_center_trans_costs in enumerate(
                        random_products_trans_cost[i]
                    )
                },
                fixed_cost=random_fixed_cost[i],
                product_capacity=random_product_capacity[i],
                dist_centers_distances=random_dist_centers_distances[i],
                opening_env_impact=random_opening_env_impact[i],
                products_trans_env_impact={
                    product_index: dist_center_impact
                    for product_index, dist_center_impact in enumerate(
                        random_products_trans_env_impact[i]
                    )
                },
                prop_delivery_risk=random_prop_delivery_risk[i],
                delivery_risk_impact=random_delivery_risk_impact[i],
            )
            facilities.append(facility)
        return facilities


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
    def get_random_echelon(cls, howmany=5, number_of_products=5, number_of_markets=5):
        random_products_trans_cost = (
            np.random.rand(howmany, number_of_products, number_of_markets) * 100
        )
        random_fixed_cost = np.random.rand(howmany) * 1000
        random_product_capacity = np.random.rand(howmany, number_of_products) * 500
        random_market_distances_distances = (
            np.random.rand(howmany, number_of_markets) * 100
        )
        random_opening_env_impact = np.random.rand(howmany) * 1000
        random_products_trans_env_impact = (
            np.random.rand(howmany, number_of_products) * 1000
        )
        random_selling_prices = np.random.rand(
            howmany, number_of_products, number_of_markets
        )
        random_prop_delivery_risk = np.random.rand(howmany, number_of_products) * 1000
        random_delivery_risk_impact = np.random.rand(howmany, number_of_products) * 1000
        facilities = list()
        for i in range(howmany):
            facility = cls(
                products_trans_cost={
                    product_index: market_trans_costs
                    for product_index, market_trans_costs in enumerate(
                        random_products_trans_cost[i]
                    )
                },
                fixed_cost=random_fixed_cost[i],
                product_capacity=random_product_capacity[i],
                market_distances=random_market_distances_distances[i],
                opening_env_impact=random_opening_env_impact[i],
                products_trans_env_impact={
                    product_index: market_impact
                    for product_index, market_impact in enumerate(
                        random_products_trans_env_impact[i]
                    )
                },
                selling_prices={
                    product_index: market_prices
                    for product_index, market_prices in enumerate(
                        random_selling_prices[i]
                    )
                },
                prop_delivery_risk=random_prop_delivery_risk[i],
                delivery_risk_impact=random_delivery_risk_impact[i],
            )
            facilities.append(facility)
        return facilities


@dataclass
class SupplyChainNetwork:
    suppliers_echelon: List = field(default_factory=SupplierFacility.get_random_echelon)
    plants_echelon: List = field(default_factory=PlantFacility.get_random_echelon)
    warehouses_echelon: List = field(
        default_factory=WarehouseFacility.get_random_echelon
    )
    distribution_centers_echelon: List = field(
        default_factory=DistributionCenterFacility.get_random_echelon
    )

    @property
    def echelons(self):
        return [
            self.suppliers_echelon,
            self.plants_echelon,
            self.warehouses_echelon,
            self.distribution_centers_echelon,
        ]

    @staticmethod
    def echelon_greedy_sort(echelon):
        """
        This function will return the echelon facilities sorted based on the greedy formula proposed in the greedy initial solution,
        """
        sorted_facilities = sorted(
            echelon,
            key=lambda facility: (facility.fixed_cost / facility.capacity.sum())
            * facility.transportation_cost,
        )
        return sorted_facilities

    def apply_initial_greedy_solution(self, demand=1000):
        echelons = self.echelons[::-1]
        # close all facilities except
        for echelon in echelons:
            for facility in echelon:
                facility.is_open = False
        for k in range(len(echelons)):
            echelon = echelons[k]
            echelon_open_facilities_capacity = 0
            sorted_echelon = SupplyChainNetwork.echelon_greedy_sort(echelon)
            for facility in sorted_echelon:
                if echelon_open_facilities_capacity < demand:
                    facility.is_open = 1
                    echelon_open_facilities_capacity += facility.capacity.sum()
                else:
                    break

    def describe(self):
        table = BeautifulTable()
        for echelon in self.echelons:
            table.columns.append([facility.is_open for facility in echelon])
        table.columns.header = [
            f"{echelon[0].__class__.__name__}s" for echelon in self.echelons
        ]
        table.set_style(BeautifulTable.STYLE_MARKDOWN)
        print(table)
