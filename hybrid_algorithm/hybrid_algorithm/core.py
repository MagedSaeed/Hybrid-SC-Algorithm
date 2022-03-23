import copy
import logging
import math
from functools import lru_cache

from hybrid_algorithm.hybrid_algorithm.vns import VNS
from hybrid_algorithm.lp_model import LPModel

from .util import Solution, TabuList


class HybridAlgorithm:
    def __init__(
        self,
        network,
        T=100,
        Tf=10,
        alpha=0.9,
        K=5,
        tabu_size=15,
        number_of_nighbors=5,
        neighbors_percentage=0.15,
        x=0.2,
        lp_model_class=LPModel,
        h=3,
    ):
        self.net = network
        self.T = T
        self.Tf = Tf
        self.alpha = alpha
        self.K = int(K)
        self.tabu_size = tabu_size
        self.tabu_list = TabuList(self.tabu_size)
        self.number_of_nighbors = number_of_nighbors
        self.neighbors_percentage = neighbors_percentage
        self.x = x
        self.h = h
        self.lp_model_class = lp_model_class
        self.original_net = copy.deepcopy(network)
        self.best_solution = None
        assert (
            self.number_of_nighbors > 0
        ), "number of neighbors should be greater than 0"

    def transition_probability(self, current_solution, candidate_solution):
        Z = self.evaluate_solution(candidate_solution)
        Z_prime = self.evaluate_solution(current_solution)
        E_delta = ((Z - Z_prime) / Z_prime) * 100
        return math.exp(-E_delta / self.T)

    @property
    @lru_cache
    def _private_network(self):
        """
        This network is used for internal calculations.
        It is initiated from the original one
        """
        return copy.deepcopy(self.net)

    @lru_cache(maxsize=None)
    def evaluate_solution(self, solution):
        # assign the solution
        self._private_network.apply_solution(solution._list)
        # evaluate it
        temp_model = self.lp_model_class(self._private_network)
        solution_objective_value = temp_model.multi_objective_value
        # clean stuff
        del temp_model
        # handler the case where there is no solution
        if solution_objective_value <= 0:
            return float("inf")
        return solution_objective_value

    @lru_cache(maxsize=None)
    def evaluate_solution_greedy(self, solution):
        network = self._private_network
        network.apply_solution(solution)
        greedy_value = 0
        for echelon in network.echelons:
            for facility in echelon:
                if facility.is_open:
                    greedy_value += facility.greedy_rank()
        return greedy_value

    def get_backtracked_solution(self, current_solution):
        parent_solution = current_solution.parent
        if parent_solution is None:
            return None
        parent_solution.childs.remove(current_solution)
        if len(parent_solution.childs) > 0:
            return parent_solution.childs[0]
        return self.get_backtracked_solution(parent_solution)

    def check_dominant_solution(self, current_solution):
        # only look check for dominant childs if they exists
        if len(current_solution.childs) > 0:
            # the best solution is the first as they are sorted based on their objective value
            best_solution_candidate = current_solution.childs[0]
            if self.evaluate_solution(best_solution_candidate) < self.evaluate_solution(
                current_solution
            ) or self.x < self.transition_probability(
                current_solution, best_solution_candidate
            ):
                # if it is not in the tabu list, add it
                if best_solution_candidate not in self.tabu_list:
                    self.tabu_list.append(best_solution_candidate)
                    logging.debug(
                        f"updating current solution to: {self.evaluate_solution(best_solution_candidate)}",
                    )
                    return best_solution_candidate
        return current_solution

    def optimize(self, current_solution=None):
        network = self.net
        if current_solution is None:
            network.apply_initial_greedy_solution()
            current_solution = Solution(network.facilities_statuses)
        logging.info(
            f"initial solution: {current_solution}, value: {self.evaluate_solution(current_solution)}"
        )
        # add current solution to tabu list
        self.tabu_list.append(current_solution)
        if self.best_solution is None:
            self.best_solution = current_solution
        else:
            if self.evaluate_solution(self.best_solution) > self.evaluate_solution(
                current_solution
            ):
                self.best_solution = current_solution

        while self.T > self.Tf:
            k = 0
            while k < self.K:
                network.apply_solution(current_solution)
                vns = VNS(network)
                # -------------------------------
                # find neighbors
                # -------------------------------
                neighbors = vns.generate_sorted_non_tabu_solutions(
                    K=self.number_of_nighbors,
                    tabu_list=self.tabu_list,
                    sorting_function=self.evaluate_solution_greedy,
                    sorting_reversed=True,
                    generation_methods=VNS.SolutionGenerationMethods.SHAKING_METHODS,
                )
                # -------------------------------
                # backtracking if no selected solution found
                # -------------------------------
                # if there is no selected solution,
                if len(neighbors) == 0:
                    # backtrack
                    logging.debug("No shaking solutions found. Backtracking..")
                    backtracked_solution = self.get_backtracked_solution(
                        current_solution
                    )
                    return self.optimize(current_solution=backtracked_solution)

                # add best h solutions to the tabu list
                self.tabu_list.extend(neighbors[: self.h])
                logging.debug(f"tabu list size: {len(self.tabu_list)}")

                # make best h solutions as childs to the current solutions
                current_solution.add_childs_solutions(neighbors[: self.h])

                # sort childs based on their lp_model evaluation
                current_solution.childs.sort(key=self.evaluate_solution)

                # see if one of the childs dominates the current solution. This
                # also includes the transition anealing hea
                current_solution = self.check_dominant_solution(current_solution)

                # see if the new current solution is better than our best solution.
                # if so, update our best solution
                if self.evaluate_solution(self.best_solution) > self.evaluate_solution(
                    current_solution
                ):
                    self.best_solution = current_solution
                    logging.info(
                        f"chaning best solution to {self.evaluate_solution(self.best_solution)}"
                    )
                # -------------------------------
                # Local Search
                # -------------------------------
                network.apply_solution(current_solution)
                local_vns = VNS(network)
                local_neighbors = local_vns.generate_sorted_non_tabu_solutions(
                    K=self.K,
                    tabu_list=self.tabu_list,
                    sorting_function=self.evaluate_solution,
                    sorting_reversed=False,
                    generation_methods=VNS.SolutionGenerationMethods.LOCAL_SEARCH_METHODS,
                )

                # keep all local neighbors
                current_solution.add_childs_solutions(local_neighbors)

                # sort childs based on their lp_model evaluation
                current_solution.childs.sort(key=self.evaluate_solution)

                # see if the new current solution is better than our best solution.
                # if so, update our best solution
                current_solution = self.check_dominant_solution(current_solution)
                if self.evaluate_solution(self.best_solution) > self.evaluate_solution(
                    current_solution
                ):
                    self.best_solution = current_solution
                    logging.info(
                        f"chaning best solution to {self.evaluate_solution(self.best_solution)}"
                    )
                logging.debug(
                    f"current solution: {current_solution}, value: {self.evaluate_solution(current_solution)}"
                )
                logging.debug(
                    f"best solution up to now: {self.best_solution} value: {self.evaluate_solution(self.best_solution)}"
                )
                logging.debug(f"updating k from {k} to {k+1}")
                k += 1
            logging.debug(f'{"previous T".center(40, "-")}{self.T}')
            self.T *= self.alpha
            logging.info(f'{"new T".center(40, "-")}{self.T}')
            logging.info(
                f"best solution up to now: {self.best_solution} value: {self.evaluate_solution(self.best_solution)}"
            )
        return self.best_solution
