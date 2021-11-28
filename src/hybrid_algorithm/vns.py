import random


class VNS:
    def __init__(self, network):
        self.net = network
        self.echelons_to_apply = random.sample(
            self.net.echelons,
            random.randint(
                1,
                len(self.net.echelons),
            ),
        )

    def move_inversion_shaking(self):
        for echelon in self.echelons_to_apply:
            # randomly select a sequence
            lower_index = random.randint(0, len(echelon) - 1)
            higher_index = random.randint(lower_index, len(echelon))
            facilities = echelon[lower_index:higher_index]
            # inverse
            for facility in facilities:
                facility.is_open = (facility.is_open + 1) % 2

    def multiple_swaps_shaking(self, iterations=1):
        for echelon in self.echelons_to_apply:
            # randomly select the number of pairs
            number_of_pairs = random.randint(1, len(echelon) // 2)
            # select random elements
            random_elements = random.sample(echelon, number_of_pairs * 2)
            # randomly pair them
            elements_pairs = []
            for index in range(number_of_pairs):
                elements_pairs.append(
                    (
                        random_elements[index],
                        random_elements[-(index + 1)],
                    )
                )
            # swap
            for _ in range(iterations):
                for pair in elements_pairs:
                    first_element, second_element = pair
                    first_element.is_open, second_element.is_open = (
                        second_element.is_open,
                        first_element.is_open,
                    )

    def two_exchange_local_search(self):
        for echelon in self.echelons_to_apply:
            # make sure one element at least is open
            if sum(f.is_open for f in echelon) > 0:
                # select an open element randomly
                first_element = random.choice(echelon)
                while first_element.is_open == 0:
                    first_element = random.choice(echelon)
                # select a closed element randomly
                second_element = random.choice(echelon)
                while second_element.is_open == 1:
                    second_element = random.choice(echelon)
                # exchange their values
                first_element.is_open = 0
                second_element.is_open = 1

    def adjacent_swap_local_search(self):
        for echelon in self.echelons_to_apply:
            # select the index of the random element
            random_element_index = random.choice(range(len(echelon)))
            # select the index of the nearest element to the selected random element
            if random_element_index == 0:
                nearest_element_index = random_element_index + 1
            else:
                nearest_element_index = random_element_index - 1
            # swap them
            echelon[random_element_index], echelon[nearest_element_index] = (
                echelon[nearest_element_index],
                echelon[random_element_index],
            )
