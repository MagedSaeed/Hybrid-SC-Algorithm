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
        x=0.2,
        lp_model_class=LPModel,
        h=3,
    ):
        self.net = network
        self.T = T
        self.Tf = Tf
        self.alpha = alpha
        self.K = K
        self.tabu_size = tabu_size
        self.tabu_list = TabuList(self.tabu_size)
        self.number_of_nighbors = number_of_nighbors
        self.x = x
        self.h = h
        self.original_net = copy.deepcopy(network)
        self.best_solution = None

    def transition_probability(self, current_solution, candidate_solution):
        Z = self.evaluate_solution(candidate_solution)
        Z_prime = self.evaluate_solution(current_solution)
        E_delta = ((Z - Z_prime) / Z_prime) * 100
        return math.exp(-E_delta / self.T)
    
    @property
    @lru_cache
    def temp_net(self):
        return copy.deepcopy(self.net)

    @lru_cache(maxsize=None)
    def evaluate_solution(self, solution):
        # assign the solution
        self.temp_net.apply_solution(solution._list)
        # evaluate it
        temp_model = LPModel(self.temp_net)
        # clean stuff
        del temp_model
        solution_objective_value = temp_model.multi_objective_value
        # handler the case where there is no solution
        if solution_objective_value <= 0:
            return float("inf")
        return solution_objective_value

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
        network = copy.deepcopy(self.net)
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
        logging.info(
            f"initial solution: {current_solution}, value: {self.evaluate_solution(current_solution)}"
        )
        # add current solution to tabu list
        self.tabu_list.append(current_solution)
        if self.best_solution is None:
            self.best_solution = copy.deepcopy(current_solution)
        else:
            if self.evaluate_solution(self.best_solution) > self.evaluate_solution(
                current_solution
            ):
                self.best_solution = current_solution

        while self.T > self.Tf:
            k = 0
            while k < self.K:
                for shaking_method in (
                    "move_inversion_shaking",
                    "multiple_swaps_shaking",
                ):
                    # -------------------------------
                    # find neighbors
                    # -------------------------------
                    for _ in range(self.number_of_nighbors):
                        # shake
                        getattr(vns, shaking_method)()
                        # save the solution to the explored solutions
                        current_solution.add_child_solution(
                            Solution(network.facilities_statuses)
                        )
                # exclude corrupted and tabu solutions
                current_solution.childs = list(
                    filter(
                        lambda solution: self.evaluate_solution(solution)
                        != float("inf")
                        and solution not in self.tabu_list,
                        current_solution.childs,
                    )
                )
                # sort solutions based on their evaluation, i.e. objective value
                current_solution.childs.sort(key=self.evaluate_solution)

                # -------------------------------
                # backtracking if no selected solution found
                # -------------------------------
                # if there is no selected solution,
                if len(current_solution.childs) == 0:
                    # backtrack
                    logging.debug("No shaking solutions found. Backtracking..")
                    backtracked_solution = self.get_backtracked_solution(
                        current_solution
                    )
                    return self.optimize(current_solution=backtracked_solution)

                # add best h solutions to the tabu list
                self.tabu_list.extend(current_solution.childs[: self.h])
                logging.debug(f"tabu list size: {len(self.tabu_list)}")

                current_solution = self.check_dominant_solution(current_solution)
                if self.evaluate_solution(self.best_solution) > self.evaluate_solution(
                    current_solution
                ):
                    self.best_solution = copy.deepcopy(current_solution)
                    logging.info(
                        f"chaning best solution to {self.evaluate_solution(self.best_solution)}"
                    )
                # -------------------------------
                # Local Search
                # -------------------------------
                for local_search_method in (
                    "two_exchange_local_search",
                    "adjacent_swap_local_search",
                ):
                    for _ in range(self.number_of_nighbors):
                        # local_search
                        getattr(vns, local_search_method)()
                        # save the solution to the explored solutions
                        current_solution.add_child_solution(
                            Solution(network.facilities_statuses)
                        )
                # exclude corrupted and tabu solutions
                current_solution.childs = list(
                    filter(
                        lambda solution: self.evaluate_solution(solution)
                        != float("inf")
                        and solution not in self.tabu_list,
                        current_solution.childs,
                    )
                )
                # sort solutions based on their evaluation, i.e. objective value
                current_solution.childs.sort(key=self.evaluate_solution)
                # keep only the best h childs
                current_solution.childs = current_solution.childs[: self.h]

                current_solution = self.check_dominant_solution(current_solution)
                if self.evaluate_solution(self.best_solution) > self.evaluate_solution(
                    current_solution
                ):
                    self.best_solution = copy.deepcopy(current_solution)
                    logging.info(
                        f"chaning best solution to {self.evaluate_solution(self.best_solution)}"
                    )
                logging.debug(
                    "current solution: {current_solution}, value: {self.evaluate_solution(current_solution)}"
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
