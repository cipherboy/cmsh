from typing import Optional

class model:
    def __init__(self): ...
    def cnf(self, var: int) -> int: ...
    def config_conflicts(self, max_conflicts: int) -> None: ...
    def config_timeout(self, max_time: float) -> None: ...
    def delete_model(self) -> None: ...
    def num_cnf_clauses(self) -> int: ...
    def num_cnf_vars(self) -> int: ...
    def num_constraint_vars(self) -> int: ...
    def num_constraints(self) -> int: ...
    def solve(self) -> Optional[bool]: ...
    def v_and(self, left: int, right: int) -> int: ...
    def v_nand(self, left: int, right: int) -> int: ...
    def v_nor(self, left: int, right: int) -> int: ...
    def v_or(self, left: int, right: int) -> int: ...
    def v_xor(self, left: int, right: int) -> int: ...
    def v_assert(self, var: int) -> None: ...
    def v_assume(self, var: int) -> None: ...
    def v_unassume(self, var: int) -> None: ...
    def val(self, var: int) -> bool: ...
    def var(self) -> int: ...
