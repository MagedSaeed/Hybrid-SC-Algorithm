from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np
from hybrid_algorithm.facilities.base_facility import BaseFacility
from hybrid_algorithm.facilities.raw_materials import RawMaterial


@dataclass
class SupplierFacility(BaseFacility):  # supplier object s
    raw_materials: List[RawMaterial]
    material_purchase_cost: List  # CCst purchase cost of raw material t from supplier s; (15*rand+10)
    material_trans_cost: Dict  # CBsit transportation cost of raw material t per km between supplier s and plant i; (0.35rand+1.2)
    material_capacity: List  # Cst capacity of supplier s for raw material t;
    plants_distances: List  # Tsi the distance between supplier s and plant at location i
    material_trans_env_impact: Dict  # ETSsit environmental impact per unit and per distance caused by transporting raw material t from supplier s to plant i;
    prop_delivery_risk: List  # Prdst probability of delivery risk for raw material t from supplier s;
    prop_quality_risk: List  # Prqst probability of quality risk for raw material t from supplier s;
    delivery_risk_impact: List  # IRDst impact caused by risk of delivery for raw material t from supplier s;
    quality_risk_impact: List  # IRQst impact caused by risk of quality for raw material t from supplier s;
    fixed_cost: float
    is_open: int = field(default=0)

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
    def get_random_echelon(cls):
        cls._configure()
        howmany = cls.NUMBER_OF_SUPPLIERS
        number_of_plants = cls.NUMBER_OF_PLANTS
        raw_materials = RawMaterial.get_random_materials()
        random_material_purchase_cost = (
            15 * np.random.rand(howmany, len(raw_materials)) + 10
        )
        random_material_trans_cost = (
            0.35 * np.random.rand(howmany, number_of_plants, len(raw_materials)) + 1.2
        )
        random_material_trans_cost = (
            0.18
            * np.tile(
                np.tile(
                    np.random.rand(len(raw_materials)).reshape(1, len(raw_materials)),
                    (number_of_plants, 1),
                ),
                (howmany, 1, 1),
            )
            + 1.1
        )
        random_material_capacity = (
            1 * np.random.rand(howmany, len(raw_materials)) + 100_000
        )
        random_plants_distances = 3 * np.random.rand(howmany, number_of_plants) + 35.35
        # random_material_trans_env_impact = (
        #     0.75
        #     * np.random.rand(
        #         howmany,
        #         number_of_plants,
        #         len(raw_materials),
        #     )
        #     + 2
        # )

        random_material_trans_env_impact = np.array(
            [
                np.tile(
                    0.75 * np.random.rand(number_of_plants).reshape(number_of_plants, 1)
                    + 2,
                    (1, len(raw_materials)),
                )
                for _ in range(howmany)
            ]
        )

        random_prop_delivery_risk = np.random.rand(howmany, len(raw_materials))
        random_prop_quality_risk = (
            0.6 * np.random.rand(howmany, len(raw_materials)) + 0.1
        )
        random_delivery_risk_impact = (
            210000 * np.random.rand(howmany, len(raw_materials)) + 50000
        )
        random_quality_risk_impact = (
            200_000 * np.random.rand(howmany, len(raw_materials)) + 220_000
        )
        random_fixed_costs = 70_000 * np.random.rand(howmany) + 50_000
        facilities = list()
        for i in range(howmany):
            facility = cls(
                raw_materials=raw_materials,
                material_purchase_cost=random_material_purchase_cost[i],
                material_trans_cost={
                    plant_index: materials_trans_costs
                    for plant_index, materials_trans_costs in enumerate(
                        random_material_trans_cost[i]
                    )
                },
                material_capacity=random_material_capacity[i],
                plants_distances=random_plants_distances[i],
                material_trans_env_impact={
                    plant_index: material_impact
                    for plant_index, material_impact in enumerate(
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
