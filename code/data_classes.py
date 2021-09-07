class Facility:
    def __init__(
        self,
        establishment_cost=0,
        capacity=0,
        transportation_cost=dict(),
    ):
        self.establishment_cost = establishment_cost
        self.capacity = capacity
        self.transportation_cost = transportation_cost
        self.is_open = False


class Echelon:
    def __init__(self, facilities, demand):
        self.facilities = facilities
        self.demand = demand

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
