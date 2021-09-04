import random

from .data_classes import Echelon, Facility

# set the random seed
random.seed(10)

suppliers_echelon = Echelon(facilities=list())
plants_echelon = Echelon(facilities=list())
warehouses_echelon = Echelon(facilities=list())
distribution_centers_echelon = Echelon(facilities=list())
customers_echelon = Echelon(facilities=list())

# let us say that we have 5 facilities for each echelon

for echelon in [
    suppliers_echelon,
    plants_echelon,
    warehouses_echelon,
    distribution_centers_echelon,
    customers_echelon,
]:
    # fill the facilities for each echelon
    for _ in range(5):
        facility = Facility(
            establishment_cost=random.randint(100, 1000),
            capacity=random.randint(100, 1000),
        )
        echelon.facilities.append(facility)
    # fill the transportation cost between facilities
    # TODO


def get_initial_solution():
    pass
