import math
from vns import VNS
from lp_model import LPModel
from util import TabuList, Solution

# Algorithm parameters:
T = 100
Tf = 10
alpha = 0.3
K = 2
tabu_size = 5
tabu_list = TabuList(tabu_size)
h = 3
number_of_nighbors = 5
best_nighbors = []
x = 0.4


class HybridAlgorithm:
    def __init__(self, network):
        self.net = network
        self.original_net = network.copy()
        self.model = LPModel(self.net)

    def transition_probability(self, current_solution, candidate_solution):
        Z = self.evaluate_solution(candidate_solution)
        Z_prime = self.evaluate_solution(current_solution)
        E_delta = ((Z - Z_prime) / Z_prime) * 100
        return math.exp(-E_delta / T)

    def evaluate_solution(self, solution):
        # assign the solution
        temp_net = self.original_net.copy()
        for echelon_statuses, echelon_facilities in zip(
            solution, self.temp_net.echelons
        ):
            for status, facility in zip(echelon_statuses, echelon_facilities):
                facility.is_open = status
        # evaluate it
        temp_model = LPModel(temp_net)
        solution_objective_value = temp_model.multi_objective_value
        # clean stuff
        del temp_model
        del temp_net
        return solution_objective_value

    def get_backtracked_solution(self, current_solution):
        parent_solution = current_solution.parent
        parent_solution.childs.remove(current_solution)
        if len(parent_solution.childs) > 0:
            return parent_solution.childs[0]
        else:
            if parent_solution is None:
                return None
            return self.get_backtracked_solution(parent_solution)

    def check_dominant_solution(self, current_solution):
        # the best solution is the first as they are sorted based on their objective value
        best_solution_candidate = current_solution.childs[0]
        if self.evaluate_solution(best_solution_candidate) < self.evaluate_solution(
            current_solution
        ):
            return best_solution_candidate
        elif x < self.transition_probability(current_solution, best_solution_candidate):
            return best_solution_candidate
        return current_solution

    def optimize(self, current_solution=None):
        network = self.net.copy()
        if current_solution is None:
            network.apply_initial_greedy_solution()
            current_solution = (
                Solution(network.facilities_statuses)
                if current_solution is None
                else current_solution
            )
        else:
            network.apply_solution(current_solution)
        vns = VNS(network)
        for shaking_method in ("move_inversion_shaking", "multiple_swaps_shaking"):
            # -------------------------------
            # find neighbors
            # -------------------------------
            for _ in range(number_of_nighbors):
                # shake
                getattr(vns, shaking_method)
                # save the solution to the explored solutions
                current_solution.add_child_solution(
                    Solution(network.facilities_statuses)
                )
            # sort solutions based on their evaluation, i.e. objective value
            current_solution.childs.sort(key=self.evaluate_solution)
            # filter non tabu solutions
            current_solution.childs = list(
                filter(
                    lambda solution: solution not in tabu_list,
                    current_solution.childs,
                )
            )

            # -------------------------------
            # backtracking if no selected solution found
            # -------------------------------
            # if there is no selected solution,
            if len(current_solution.childs) == 0:
                # backtrack
                backtracked_solution = self.get_backtracked_solution(current_solution)
                self.optimize(current_solution=backtracked_solution)
            self.check_dominant_solution(current_solution)
            # -------------------------------
            # Local Search
            # -------------------------------
            for local_search_method in (
                "two_exchange_local_search",
                "adjacent_swap_local_search",
            ):
                for _ in range(number_of_nighbors):
                    # local_search
                    getattr(vns, shaking_method)
                    # save the solution to the explored solutions
                    current_solution.add_child_solution(
                        Solution(network.facilities_statuses)
                    )
                # sort solutions based on their evaluation, i.e. objective value
                current_solution.childs.sort(key=self.evaluate_solution)
                # filter non tabu solutions
                current_solution.childs = list(
                    filter(
                        lambda solution: solution not in tabu_list,
                        current_solution.childs,
                    )
                )
                self.check_dominant_solution(current_solution)
