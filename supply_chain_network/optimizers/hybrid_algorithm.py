import sys
import copy
import logging
import math
from functools import cached_property, lru_cache

from .vns import VNS
from .lp_model import LPModel
from supply_chain_network import SupplyChainNetwork
from .utils import Solution, TabuList


class HybridAlgorithm:
    def __init__(
        self,
        network,
        T=100,
        Tf=10,
        alpha=0.9,
        K=5,
        tabu_size=15,
        number_of_neighbors=5,
        minimum_number_of_neighbors=5,
        neighbors_percentage=0.15,
        x=0.2,
        lp_model_class=LPModel,
        h=3,
        max_recursion_limit=5000,
    ):
        self.net = network
        self.T = T
        self.Tf = Tf
        self.alpha = alpha
        self.K = int(K)
        self.tabu_size = tabu_size
        self.tabu_list = TabuList(self.tabu_size)
        self.number_of_neighbors = number_of_neighbors
        self.neighbors_percentage = neighbors_percentage
        self.minimum_number_of_neighbors = minimum_number_of_neighbors
        self.x = x
        self.h = h
        self.lp_model_class = lp_model_class
        self.original_net = copy.deepcopy(network)
        self.best_solution = None
        self._intermediate_solutions = set()
        self.max_recursion_limit = max_recursion_limit
        sys.setrecursionlimit(self.max_recursion_limit)

        assert (
            self.number_of_neighbors > 0
        ), "number of neighbors should be greater than 0"

    def transition_probability(self, current_solution, candidate_solution):
        Z = self.evaluate_solution_optimal(candidate_solution)
        Z_prime = self.evaluate_solution_optimal(current_solution)
        E_delta = ((Z - Z_prime) / Z_prime) * 100
        # this is to bypass a math range error (an overflow error)
        exponent = min(-E_delta / self.T, 700)
        return math.exp(exponent)

    @cached_property
    def _private_network(self):
        """
        This network is used for internal calculations.
        It is initiated from the original one
        """
        return SupplyChainNetwork.make_a_copy(self.net)

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
            if self.evaluate_solution_optimal(
                best_solution_candidate
            ) < self.evaluate_solution_optimal(
                current_solution
            ) or self.x < self.transition_probability(
                current_solution,
                best_solution_candidate,
            ):
                # if it is not in the tabu list, add it
                if best_solution_candidate not in self.tabu_list:
                    self.tabu_list.append(best_solution_candidate)
                    logging.debug(
                        f"updating current solution to: {self.evaluate_solution_optimal(best_solution_candidate)}",
                    )
                    self._intermediate_solutions.add(best_solution_candidate)
                    return best_solution_candidate
        return current_solution

    @lru_cache(maxsize=2**22)
    def evaluate_solution_optimal(self, solution):
        return Solution.evaluate_solution_optimal(
            solution=solution,
            network=self._private_network,
        )

    @lru_cache(maxsize=2**22)
    def evaluate_solution_greedy(self, solution):
        return Solution.evaluate_solution_greedy(
            solution=solution,
            network=self._private_network,
        )

    def optimize(self, current_solution=None, return_intermediate_solutions=True):
        network = self.net
        if current_solution is None:
            network.apply_initial_greedy_solution()
            current_solution = Solution(network.facilities_statuses)
        logging.info(
            f"initial solution: {current_solution}, value: {self.evaluate_solution_optimal(current_solution)}"
        )
        # add current solution to tabu list
        self.tabu_list.append(current_solution)
        if self.best_solution is None:
            self.best_solution = current_solution
        else:
            if self.evaluate_solution_optimal(
                self.best_solution
            ) > self.evaluate_solution_optimal(current_solution):
                self.best_solution = current_solution
                logging.info(
                    f"changing best solution to {self.evaluate_solution_optimal(self.best_solution)}"
                )
        logging.info(f"value of K is: {self.K}")
        while self.T > self.Tf:
            k = 0
            while k < self.K:
                # -------------------------------
                # find neighbors
                # -------------------------------
                neighbors = VNS.generate_sorted_non_tabu_solutions(
                    solution=current_solution,
                    number_of_neighbors=int(self.number_of_neighbors),
                    neighbors_percentage=self.neighbors_percentage,
                    min_neighbors_per_generation_method=self.minimum_number_of_neighbors,
                    tabu_list=self.tabu_list,
                    sorting_function=self.evaluate_solution_optimal,
                    sorting_reversed=True,
                    generation_methods=VNS.SolutionGenerationMethods.SHAKING_METHODS,
                )
                # -------------------------------
                # backtracking if no selected solution found
                # -------------------------------
                # if there is no selected solution,
                if len(neighbors) == 0:
                    # backtrack
                    logging.info("No shaking solutions found. Backtracking..")
                    backtracked_solution = self.get_backtracked_solution(
                        current_solution
                    )
                    # if the backtracked solution is None, restart the algorithm
                    if backtracked_solution is None:
                        try:
                            return self.optimize()
                        except RecursionError as e:
                            logging.warning(
                                f"The algorithm reached to its max depth recursion. No further backtracking is possible with the given maximum recursion limit ({self.max_recursion_limit}) The latest solution will be returned"
                            )
                            if return_intermediate_solutions:
                                return self.best_solution, self._intermediate_solutions
                            return self.best_solution
                    if self.evaluate_solution_optimal(
                        self.best_solution
                    ) > self.evaluate_solution_optimal(backtracked_solution):
                        self.best_solution = backtracked_solution
                        logging.info(
                            f"changing best solution to {self.evaluate_solution_optimal(self.best_solution)}"
                        )
                    try:
                        return self.optimize()
                    except RecursionError as e:
                        logging.warning(
                            f"The algorithm reached to its max depth recursion. No further backtracking is possible with the given maximum recursion limit ({self.max_recursion_limit}) The latest solution will be returned"
                        )
                        if return_intermediate_solutions:
                            return self.best_solution, self._intermediate_solutions
                        return self.best_solution

                # add best h solutions to the tabu list
                self.tabu_list.extend(neighbors[: self.h])
                logging.info(f"tabu list size: {len(self.tabu_list)}")

                # make best h solutions as childs to the current solutions
                current_solution.add_childs_solutions(neighbors[: self.h])

                # filter out corrupted solutions
                current_solution.childs = list(
                    filter(
                        lambda solution: self.evaluate_solution_optimal(solution)
                        != float("inf"),
                        current_solution.childs,
                    )
                )

                # sort childs based on their lp_model evaluation
                current_solution.childs.sort(key=self.evaluate_solution_optimal)

                # see if one of the childs dominates the current solution. This
                # also includes the transition anealing hea
                current_solution = self.check_dominant_solution(current_solution)

                # see if the new current solution is better than our best solution.
                # if so, update our best solution
                if self.evaluate_solution_optimal(
                    self.best_solution
                ) > self.evaluate_solution_optimal(current_solution):
                    self.best_solution = current_solution
                    logging.info(
                        f"chaning best solution to {self.evaluate_solution_optimal(self.best_solution)}"
                    )
                # -------------------------------
                # Local Search
                # -------------------------------
                local_neighbors = VNS.generate_sorted_non_tabu_solutions(
                    solution=current_solution,
                    number_of_neighbors=int(self.number_of_neighbors),
                    neighbors_percentage=self.neighbors_percentage,
                    min_neighbors_per_generation_method=self.minimum_number_of_neighbors,
                    tabu_list=self.tabu_list,
                    sorting_function=self.evaluate_solution_optimal,
                    sorting_reversed=False,
                    generation_methods=VNS.SolutionGenerationMethods.LOCAL_SEARCH_METHODS,
                )

                # keep best h local neighbors
                current_solution.add_childs_solutions(local_neighbors[: self.h])

                # filter out corrupted solutions
                current_solution.childs = list(
                    filter(
                        lambda solution: self.evaluate_solution_optimal(solution)
                        != float("inf"),
                        current_solution.childs,
                    )
                )

                # sort childs based on their lp_model evaluation
                current_solution.childs.sort(key=self.evaluate_solution_optimal)

                # see if the new current solution is better than our best solution.
                # if so, update our best solution
                current_solution = self.check_dominant_solution(current_solution)
                if self.evaluate_solution_optimal(
                    self.best_solution
                ) > self.evaluate_solution_optimal(current_solution):
                    self.best_solution = current_solution
                    logging.info(
                        f"changing best solution to {self.evaluate_solution_optimal(self.best_solution)}"
                    )
                logging.debug(
                    f"current solution: {current_solution}, value: {self.evaluate_solution_optimal(current_solution)}"
                )
                logging.debug(
                    f"best solution up to now: {self.best_solution} value: {self.evaluate_solution_optimal(self.best_solution)}"
                )
                logging.info(f"updating k from {k} to {k+1}")
                k += 1
            if self.evaluate_solution_optimal(
                self.best_solution
            ) > self.evaluate_solution_optimal(current_solution):
                self.best_solution = current_solution
                logging.info(
                    f"changing best solution to {self.evaluate_solution_optimal(self.best_solution)}"
                )
            logging.debug(f'{"previous T".center(40, "-")}{self.T}')
            self.T *= self.alpha
            logging.info(f'{"new T".center(40, "-")}{self.T}')
            logging.info(
                f"best solution up to now: {self.best_solution} value: {self.evaluate_solution_optimal(self.best_solution)}"
            )
        if return_intermediate_solutions:
            return self.best_solution, self._intermediate_solutions
        return self.best_solution
