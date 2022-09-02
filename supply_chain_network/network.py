from dataclasses import dataclass, field

from beautifultable import BeautifulTable
from supply_chain_network.config import AppConfig

from supply_chain_network.facilities import (
    DistributionCenterFacility,
    MarketFacility,
    PlantFacility,
    SupplierFacility,
    WarehouseFacility,
)
from supply_chain_network.utils import (
    facilities_greedy_sort,
    get_open_facilities_in_echelon,
)

FACILITIES_DEFAULT = AppConfig.config["facilities"]


@dataclass
class SupplyChainNetwork:
    facilities_count: int = field(default=int(FACILITIES_DEFAULT["facilities_count"]))
    raw_materials_count: int = field(
        default=int(FACILITIES_DEFAULT["raw_materials_count"])
    )
    markets_count: int = field(default=int(FACILITIES_DEFAULT["markets_count"]))
    products_count: int = field(default=int(FACILITIES_DEFAULT["products_count"]))

    def initialize_random_network(self):
        # rest AppConfig with the new values first
        config = AppConfig.config
        config["facilities"]["facilities_count"] = str(self.facilities_count)
        config["facilities"]["raw_meterials_count"] = str(self.raw_materials_count)
        config["facilities"]["markets_count"] = str(self.markets_count)
        config["facilities"]["products_count"] = str(self.products_count)
        AppConfig.set_config(config=config)
        # initialize echelons
        self.suppliers_echelon = SupplierFacility.get_random_echelon()
        self.plants_echelon = PlantFacility.get_random_echelon()
        self.warehouses_echelon = WarehouseFacility.get_random_echelon()
        self.distribution_centers_echelon = (
            DistributionCenterFacility.get_random_echelon()
        )
        self.markets_echelon = MarketFacility.get_random_echelon()

    @classmethod
    def initialize_network_from_echelons(
        cls,
        suppliers,
        plants,
        warehouses,
        dist_centers,
        markets,
    ):
        network = cls()
        network.suppliers_echelon = suppliers
        network.plants_echelon = plants
        network.warehouses_echelon = warehouses
        network.distribution_centers_echelon = dist_centers
        network.markets_echelon = markets
        return network

    @classmethod
    def make_a_copy(cls, network):
        return cls.initialize_network_from_echelons(
            suppliers=network.suppliers_echelon,
            plants=network.plants_echelon,
            warehouses=network.warehouses_echelon,
            dist_centers=network.distribution_centers_echelon,
            markets=network.markets_echelon,
        )

    @property
    def echelons(self):
        return [
            self.suppliers_echelon,
            self.plants_echelon,
            self.warehouses_echelon,
            self.distribution_centers_echelon,
        ]

    @property
    def market_demand(self):
        return sum(market.products_demand.sum() for market in self.markets_echelon)

    def apply_initial_greedy_solution(self):
        echelons = self.echelons[::-1]
        # close all facilities
        for echelon in echelons:
            for facility in echelon:
                facility.is_open = 0
        # previous_echelon_demand = market_demand
        for k in range(len(echelons)):
            echelon = echelons[k]
            echelon_open_facilities_capacity = 0
            sorted_echelon = facilities_greedy_sort(echelon)
            for facility in sorted_echelon:
                if echelon_open_facilities_capacity < self.market_demand:
                    facility.is_open = 1
                    echelon_open_facilities_capacity += facility.capacity.sum()
                else:
                    break
            # previous_echelon_demand = sum(
            #     facility.capacity.sum()
            #     for facility in get_open_facilities_in_echelon(echelon)
            # )

    def describe(self):
        table = BeautifulTable()
        for echelon in self.echelons:
            table.columns.append([facility.is_open for facility in echelon])
        table.columns.header = [
            f"{echelon[0].__class__.__name__}s" for echelon in self.echelons
        ]
        table.set_style(BeautifulTable.STYLE_MARKDOWN)
        print(table)

    @property
    def facilities_statuses(self):
        echelons_status = list()
        for echelon in self.echelons:
            echelons_status.append([facility.is_open for facility in echelon])
        return echelons_status

    def apply_solution(self, solution):
        for echelon_index, echelon in enumerate(solution):
            for facility_index, facility_status in enumerate(echelon):
                self.echelons[echelon_index][facility_index].is_open = facility_status