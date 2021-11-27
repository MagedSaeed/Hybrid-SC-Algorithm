from dataclasses import dataclass, field
from typing import List

from beautifultable import BeautifulTable

from facilities import (
    DistributionCenterFacility,
    MarketFacility,
    PlantFacility,
    SupplierFacility,
    WarehouseFacility,
)


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
    markets_echelon: List = field(default_factory=MarketFacility.get_random_echelon)

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

    def apply_initial_greedy_solution(self):
        demand = sum(self.markets_echelon[0].products_demand)
        echelons = self.echelons[::-1]
        # close all facilities
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
