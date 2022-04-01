from copy import deepcopy
import copy
import random
from .util import Solution, random_four_digits_binary_string


class VNS:
    class SolutionGenerationMethods:
        SHAKING_METHODS = [
            "move_inversion_shaking",
            "multiple_swaps_shaking",
        ]
        LOCAL_SEARCH_METHODS = [
            "two_exchange_local_search",
            "adjacent_swap_local_search",
        ]

    @classmethod
    def move_inversion_shaking(self, solution):
        new_solution = copy.deepcopy(solution)
        binary_string = random_four_digits_binary_string()
        for echelon, is_selected in zip(new_solution, binary_string):
            if is_selected == "0":
                continue
            # randomly select a sequence
            lower_index = random.randint(0, len(echelon) - 1)
            higher_index = random.randint(lower_index, len(echelon))
            facilities = echelon[lower_index:higher_index]
            # inverse
            for facility_index in facilities:
                echelon[facility_index] = (echelon[facility_index] + 1) % 2
        return new_solution

    @classmethod
    def multiple_swaps_shaking(self, solution, iterations=1):
        new_solution = copy.deepcopy(solution)
        binary_string = random_four_digits_binary_string()
        for echelon, is_selected in zip(new_solution, binary_string):
            if is_selected == "0":
                continue
            # randomly select the number of pairs
            number_of_pairs = random.randint(1, len(echelon) // 2)
            for _ in range(number_of_pairs):
                for _ in range(iterations):
                    first_facility_index = random.randint(1, len(echelon) - 1)
                    second_facility_index = random.randint(1, len(echelon) - 1)
                    echelon[first_facility_index], echelon[second_facility_index] = (
                        echelon[second_facility_index],
                        echelon[first_facility_index],
                    )
        return new_solution

    @classmethod
    def two_exchange_local_search(self, solution):
        new_solution = copy.deepcopy(solution)
        binary_string = random_four_digits_binary_string()
        for echelon, is_selected in zip(new_solution, binary_string):
            if is_selected == "0":
                continue
            # make sure one element at least is open and one element is at least closed
            if 0 < sum(echelon) < len(echelon):
                # select an open element randomly
                random_open_facility_index = random.choice(range(len(echelon)))
                while echelon[random_open_facility_index] == 0:
                    random_open_facility_index = random.choice(range(len(echelon)))
                # select a closed element randomly
                random_closed_facility_index = random.choice(range(len(echelon)))
                while echelon[random_closed_facility_index] == 1:
                    random_closed_facility_index = random.choice(range(len(echelon)))
                # exchange their values
                echelon[random_open_facility_index] = 0
                echelon[random_closed_facility_index] = 1
        return new_solution

    @classmethod
    def adjacent_swap_local_search(self, solution):
        new_solution = copy.deepcopy(solution)
        binary_string = random_four_digits_binary_string()
        for echelon, is_selected in zip(new_solution, binary_string):
            if is_selected == "0":
                continue
            # select the index of the random element
            random_element_index = random.choice(range(len(echelon)))
            # select the index of the nearest element to the selected random element
            nearest_element_index = random_element_index - 1
            # swap them
            echelon[random_element_index], echelon[nearest_element_index] = (
                echelon[nearest_element_index],
                echelon[random_element_index],
            )
        return new_solution

    @classmethod
    def generate_sorted_non_tabu_solutions(
        self,
        solution,
        K,
        tabu_list,
        sorting_function,
        sorting_reversed=False,
        generation_methods=SolutionGenerationMethods.SHAKING_METHODS,
    ):
        solutions = set()
        solution_list = solution._list
        for method in generation_methods:
            # -------------------------------
            # find solutions with the provided
            # solution generation methods
            # -------------------------------
            for _ in range(K):
                new_solution_list = getattr(VNS, method)(solution_list)
                solutions.add(Solution(new_solution_list))
        # exclude tabu solutions
        solutions -= set(tabu_list)
        # sort solutions based on their evaluation, i.e. objective value
        solutions = sorted(solutions, key=sorting_function, reverse=sorting_reversed)
        return solutions
