import random

from data_classes import Echelon, Facility

# set the random seed
random.seed(10)

suppliers_echelon = Echelon(
    facilities=list(),
    demand=random.randint(100, 1000),
)
plants_echelon = Echelon(
    facilities=list(),
    demand=random.randint(
        100,
        1000,
    ),
)
warehouses_echelon = Echelon(
    facilities=list(),
    demand=random.randint(100, 1000),
)
distribution_centers_echelon = Echelon(
    facilities=list(),
    demand=random.randint(
        100,
        1000,
    ),
)
customers_echelon = Echelon(
    facilities=list(),
    demand=random.randint(100, 1000),
)

# let us say that we have 5 facilities for each echelon

echelons = [
    suppliers_echelon,
    plants_echelon,
    warehouses_echelon,
    distribution_centers_echelon,
    customers_echelon,
]

for echelon in echelons:
    # fill the facilities for each echelon
    for _ in range(5):
        facility = Facility(
            establishment_cost=random.randint(100, 1000),
            capacity=random.randint(100, 1000),
        )
        echelon.facilities.append(facility)

for i in range(len(echelons) - 1, 0, -1):
    current_echelon = echelons[i]
    prev_echelon = echelons[i - 1]
    for c_facility in current_echelon.facilities:
        for p_facility in prev_echelon.facilities:
            transportation_cost = random.randint(100, 1000)
            c_facility.transportation_cost[p_facility] = transportation_cost
            p_facility.transportation_cost[c_facility] = transportation_cost


def get_initial_solution():
    for k in range(len(echelons) - 2, 0, -1):
        current_echelon = echelons[k]
        next_echelon = echelons[k + 1]
        current_echelon_open_facilities_capacity = 0
        for facility in current_echelon.facilities:
            if current_echelon_open_facilities_capacity < next_echelon.demand:
                facility.is_open = True
                current_echelon_open_facilities_capacity += facility.capacity
            else:
                break


get_initial_solution()
