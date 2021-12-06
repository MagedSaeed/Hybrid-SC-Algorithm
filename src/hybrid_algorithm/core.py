from vns import VNS
from lp_model import LPModel
from tabu_list import TabuList

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
        self.model = LPModel(self.net)

    def get_facilities_status(self):
        echelons_status = list()
        echelons_status.append(
            [facility.is_open for facility in self.net.suppliers_echelon]
        )
        echelons_status.append(
            [facility.is_open for facility in self.net.plants_echelon]
        )
        echelons_status.append(
            [facility.is_open for facility in self.net.warehouses_echelon]
        )
        echelons_status.append(
            [facility.is_open for facility in self.net.distribution_centers_echelon]
        )
        return echelons_status

    def transition_probability(self, generated_obj_value, original_obj_value):
        pass

    def optimize(self):
        self.net.apply_initial_greedy_solution()
        current_solution = self.get_facilities_status()
        current_objective_value = self.model.multi_objective_value
        vns = VNS(self.net)
        explored_solutions = list()
        explored_objective_values = list()
        for shaking_method in ("move_inversion_shaking", "multiple_swaps_shaking"):
            for _ in range(number_of_nighbors):
                # shake
                getattr(vns, shaking_method)
                # save the solution and its objective value
                explored_solution = self.get_facilities_status()
                explored_objective_value = self.model.multi_objective_value
                explored_solutions.append(explored_solution)
                explored_objective_values.append(explored_objective_value)
            # sort solutions based on their objective values
            sorted_explored_solutions, sorted_explored_objective_values = list(
                zip(
                    *sorted(
                        list(zip(explored_solutions, explored_objective_values)),
                        kye=lambda item: item[1],
                    )
                )
            )
            # select best h non tabu solutions
            best_h_solutions = list()
            best_h_objective_values = list()
            i = 0
            while i < h:
                if sorted_explored_solutions[i] not in tabu_list:
                    i += 1
                    best_h_solutions.append(sorted_explored_solutions[i])
                    best_h_objective_values.append(sorted_explored_objective_values[i])
            # -------------------------------
            # backtracking needs some checks
            # -------------------------------

            # If new best solution dominates the current solution
            # best_h_solutions[0] is the best solution and
            # best_h_objective_values[0] is the best objective value
            best_objective_value = best_h_objective_values[0]
            best_solution = best_h_solutions[0]
            if best_objective_value < current_objective_value:
                # the new best solution = the current solution;
                current_solution = best_solution
                current_objective_value = best_objective_value
                # update the tabu list;
                tabu_list.append(best_solution)
                # keep the best h-1 solutions
                del sorted_explored_solutions[0]
                del sorted_explored_objective_values[0]
            # elif x <