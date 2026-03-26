from src.solver.interface import solve
from src.solver.ga_solver import GAMaxRectsSolver
from src.solver.maxrects import MaxRectsSolver
from src.solver.registry import DEFAULT_SOLVER_ID, create_solver, list_solver_ids
from src.solver.skyline import SkylineSolver

__all__ = [
    "solve",
    "GAMaxRectsSolver",
    "MaxRectsSolver",
    "SkylineSolver",
    "DEFAULT_SOLVER_ID",
    "create_solver",
    "list_solver_ids",
]
