import random

from beautifultable import BeautifulTable

random.seed(10)


class Facility:
    def __init__(
        self,
        establishment_cost=0,
        capacity=0,
        transportation_cost=None,
        name="",
    ):
        self.establishment_cost = establishment_cost
        self.capacity = capacity
        self.transportation_cost = (
            transportation_cost if transportation_cost else dict()
        )
        self.is_open = False

    @classmethod
    def get_random_facilities(cls, length=5):
        facilities = list()
        for _ in range(length):
            facility = cls(
                establishment_cost=random.randint(100, 1000),
                capacity=random.randint(100, 1000),
            )
            facilities.append(facility)
        return facilities

    @staticmethod
    def fill_facilities_with_random_trans_cost(echelons):
        for i in range(len(echelons) - 1, 0, -1):
            current_echelon = echelons[i]
            prev_echelon = echelons[i - 1]
            for p_facility in prev_echelon.facilities:
                for c_facility in current_echelon.facilities:
                    transportation_cost = random.randint(100, 1000)
                    p_facility.transportation_cost[c_facility] = transportation_cost


class Echelon:
    def __init__(self, facilities=None, name="just another echelon"):
        self.facilities = facilities if facilities else list()
        self.name = name

    def greedy_sort(self, other_echelon):
        """
        This function will return the echelon facilities sorted based on the greedy formula proposed in the greedy initial solution,
        """
        sorted_facilities = sorted(
            self.facilities,
            key=lambda facility: (facility.establishment_cost / facility.capacity)
            * sum(
                [
                    cost
                    for other_facility, cost in facility.transportation_cost.items()
                    if other_facility in other_echelon.facilities
                ]
            ),
        )
        return sorted_facilities

    def total_capacity(self):
        return sum(facility.capacity for facility in self.facilities)


class SupplyChainNetwork:
    def __init__(self, demand, echelons=None):
        self.demand = demand
        self.echelons = echelons if echelons else list()

    @classmethod
    def get_random_network(cls, demand=500, seed=10):
        suppliers_echelon = Echelon(
            facilities=Facility.get_random_facilities(),
            name="suppliers echelon",
        )
        plants_echelon = Echelon(
            facilities=Facility.get_random_facilities(),
            name="plants echelon",
        )
        warehouses_echelon = Echelon(
            facilities=Facility.get_random_facilities(),
            name="warehouses echelon",
        )
        distribution_centers_echelon = Echelon(
            facilities=Facility.get_random_facilities(),
            name="distribution centers echelon",
        )
        customers_echelon = Echelon(
            facilities=Facility.get_random_facilities(), name="customers echelon"
        )
        echelons = [
            suppliers_echelon,
            plants_echelon,
            warehouses_echelon,
            distribution_centers_echelon,
            customers_echelon,
        ]
        Facility.fill_facilities_with_random_trans_cost(echelons=echelons)
        # open all customer facilities
        for facility in customers_echelon.facilities:
            facility.is_open = True
        network = cls(demand, echelons)
        return network

    def get_initial_solution(self):
        for k in range(len(self.echelons) - 2, -1, -1):
            current_echelon = self.echelons[k]
            next_echelon = self.echelons[k + 1]
            current_echelon_open_facilities_capacity = 0
            sorted_facilities = current_echelon.greedy_sort(next_echelon)
            for facility in sorted_facilities:
                if current_echelon_open_facilities_capacity < self.demand:
                    facility.is_open = True
                    current_echelon_open_facilities_capacity += facility.capacity
                else:
                    break

    def descripe(self):
        table = BeautifulTable()
        for echelon in self.echelons:
            table.columns.append([facility.is_open for facility in echelon.facilities])
        table.columns.header = [echelon.name for echelon in self.echelons]
        table.set_style(BeautifulTable.STYLE_MARKDOWN)
        print(table)
