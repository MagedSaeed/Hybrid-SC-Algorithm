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
        if parent is not None:
            parent.add_child_solution(self)

    def add_child_solution(self, solution):
        if solution not in self.childs:
            solution.parent = self
            self.childs.append(solution)

    def add_childs_solutions(self, solutions):
        self.childs.extend(solutions)

    def is_root(self):
        return self.parent is None

    def __repr__(self) -> str:
        return str(self._list)

    def __iter__(self):
        return iter(self._list)
