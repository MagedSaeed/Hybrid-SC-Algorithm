from hybrid_algorithm.config import AppConfig
from hybrid_algorithm.lp_model import LPModel
import random

from hybrid_algorithm.utils import get_three_random_weights


class TabuList(list):

    # Read-only
    @property
    def maxLen(self):
        return self._maxLen

    def __init__(self, max_length, *args, **kwargs):
        self._maxLen = max_length
        super().__init__(self, *args, **kwargs)

    def _truncate(self):
        """Called by various methods to reinforce the maximum length."""
        dif = len(self) - self._maxLen
        if dif > 0:
            self[:dif] = []

    def append(self, x):
        list.append(self, x)
        self._truncate()

    def insert(self, *args):
        list.insert(self, *args)
        self._truncate()

    def extend(self, x):
        list.extend(self, x)
        self._truncate()

    def __setitem__(self, *args):
        list.__setitem__(self, *args)
        self._truncate()

    def __setslice__(self, *args):
        list.__setslice__(self, *args)
        self._truncate()


class Solution:
    def __init__(
        self,
        solution_list=[],
        parent=None,
    ):
        self._list = solution_list
        self.childs = list()
        self.parent = parent
        self.meta_data = {}
        if parent is not None:
            parent.add_child_solution(self)

    def __hash__(self):
        return hash(frozenset(tuple(map(tuple, self._list))))

    def __eq__(self, other):
        return other._list == self._list

    def is_root(self):
        return self.parent is None

    def __repr__(self) -> str:
        return str(self._list)

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def add_child_solution(self, solution):
        if solution not in self.childs:
            solution.parent = self
            self.childs.append(solution)

    def add_childs_solutions(self, solutions):
        new_solutions = set(set(solutions) - set(self.childs))
        for solution in new_solutions:
            solution.parent = self
            self.childs.append(solution)

    def filter_solutions(self, filtering_function=None):
        self.childs = list(
            filter(
                filtering_function,
                self.childs,
            )
        )

    @staticmethod
    def evaluate_solution_greedy(solution, network):
        network.apply_solution(solution)
        greedy_value = 0
        for echelon in network.echelons:
            for facility in echelon:
                if facility.is_open:
                    greedy_value += facility.greedy_rank()
        return greedy_value

    @staticmethod
    def evaluate_solution_optimal(
        solution,
        network,
        lp_model_class=LPModel,
        evaluation_function="weighted_multi_objective_value",
    ):
        # assign random weights
        w1, w2, w3 = get_three_random_weights()
        AppConfig.config["lp_model"]["z1_weight"] = str(w1)
        AppConfig.config["lp_model"]["z2_weight"] = str(w2)
        AppConfig.config["lp_model"]["z3_weight"] = str(w3)
        solution.meta_data["z1_weight"] = w1
        solution.meta_data["z2_weight"] = w2
        solution.meta_data["z3_weight"] = w3
        # assign the solution
        network.apply_solution(solution._list)
        # check if the open facilities capacity does not serve the demand
        # if so, return not feasible
        for echelon in network.echelons:
            echelon_capacity = [
                facility.capacity.sum() for facility in echelon if facility.is_open
            ]
            if sum(echelon_capacity) < network.market_demand:
                return float("inf")
        # evaluate it using lp
        temp_model = lp_model_class(network)
        solution_objective_value = getattr(temp_model, evaluation_function)
        # clean stuff
        del temp_model
        # handler the case where there is no solution
        if solution_objective_value is None:
            return float("inf")
        return solution_objective_value


def random_four_digits_binary_string():
    binary_string = ""
    for _ in range(4):
        digit = random.randint(0, 1)
        binary_string += str(digit)
    return binary_string
