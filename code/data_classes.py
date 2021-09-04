class Facility:
    def __init__(self, establishment_cost=0, capacity=0, transportation_cost=dict()):
        self.establishment_cost = establishment_cost
        self.capacity = capacity
        self.transportation_cost = transportation_cost


class Echelon:
    def __init__(self, facilities):
        self.facilities = facilities
