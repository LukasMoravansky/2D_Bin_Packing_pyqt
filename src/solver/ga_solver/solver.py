from __future__ import annotations

from dataclasses import dataclass
import random
import time

from src.domain.problem import PackingProblem
from src.domain.solution import PackingSolution
from src.domain.item_type import ItemType
from src.solver.common.ordering import PieceJob, expand_jobs, job_orderings_for_search
from src.solver.maxrects_solver import MaxRectsSolver

Fitness = tuple[int, float]


@dataclass(frozen=True, slots=True)
class GAConfig:
    """Configuration for GA metaheuristic over MaxRects decoder."""

    population_size: int = 40
    max_generations: int = 60
    mutation_rate: float = 0.15
    elite_count: int = 2
    seed: int = 42
    patience: int = 12
    max_time_s: float = 1.5
    tournament_size: int = 3


def _job_key(job: PieceJob) -> tuple[int, int]:
    return (job.type_id, job.copy_index)


def _fitness_tuple(solution: PackingSolution) -> Fitness:
    return (solution.placed_count, -solution.unused_area)


def _fitness_better(a: Fitness, b: Fitness) -> bool:
    return a > b


class GAMaxRectsSolver:
    """
    Genetic algorithm that evolves piece order permutations and decodes every
    individual via the existing MaxRects solver.
    """

    def __init__(self, config: GAConfig | None = None) -> None:
        self.config = config or GAConfig()
        self._decoder = MaxRectsSolver()

    def solve(self, problem: PackingProblem) -> PackingSolution:
        """Run GA search; fallback to deterministic MaxRects if GA fails."""
        try:
            return self._run_ga(problem)
        except Exception:
            return self._fallback_maxrects(problem)

    def _run_ga(self, problem: PackingProblem) -> PackingSolution:
        jobs = expand_jobs(problem.item_types)
        if not jobs:
            return self._decoder.solve(problem, [])

        cfg = self.config
        start = time.perf_counter()
        deadline = start + cfg.max_time_s
        rng = random.Random(cfg.seed)

        pop_size = max(2, cfg.population_size)
        elite_count = max(1, min(cfg.elite_count, pop_size))
        tournament_size = max(2, min(cfg.tournament_size, pop_size))
        max_generations = max(1, cfg.max_generations)

        population = self._initial_population(problem.item_types, jobs, pop_size, rng)

        best_solution: PackingSolution | None = None
        best_fitness: Fitness | None = None
        stale_gens = 0

        for _ in range(max_generations):
            if time.perf_counter() >= deadline:
                break

            scored, timed_out = self._score_population(problem, jobs, population, deadline)
            if not scored:
                break
            scored.sort(key=lambda item: item[1], reverse=True)

            top_solution, top_fitness = scored[0][2], scored[0][1]
            if best_fitness is None or _fitness_better(top_fitness, best_fitness):
                best_solution = top_solution
                best_fitness = top_fitness
                stale_gens = 0
            else:
                stale_gens += 1
                if stale_gens >= cfg.patience:
                    break

            next_population: list[list[int]] = [chrom for chrom, _, _ in scored[:elite_count]]
            while len(next_population) < pop_size:
                if time.perf_counter() >= deadline:
                    break
                p1 = self._tournament_select(scored, tournament_size, rng)
                p2 = self._tournament_select(scored, tournament_size, rng)
                child = self._order_crossover(p1, p2, rng)
                self._mutate(child, cfg.mutation_rate, rng)
                next_population.append(child)
            population = next_population
            if timed_out:
                break

        if best_solution is None:
            raise RuntimeError("GA produced no solution.")
        return best_solution

    def _initial_population(
        self,
        item_types: tuple[ItemType, ...],
        jobs: list[PieceJob],
        pop_size: int,
        rng: random.Random,
    ) -> list[list[int]]:
        key_to_index = {_job_key(job): idx for idx, job in enumerate(jobs)}
        seen: set[tuple[int, ...]] = set()
        population: list[list[int]] = []

        for ordering in job_orderings_for_search(item_types):
            chrom = [key_to_index[_job_key(job)] for job in ordering]
            sig = tuple(chrom)
            if sig in seen:
                continue
            seen.add(sig)
            population.append(chrom)
            if len(population) >= pop_size:
                return population

        base = list(range(len(jobs)))
        attempts = 0
        max_attempts = max(50, pop_size * 20)
        while len(population) < pop_size and attempts < max_attempts:
            attempts += 1
            chrom = list(base)
            rng.shuffle(chrom)
            if rng.random() < 0.6:
                self._mutate(chrom, 0.7, rng)
            sig = tuple(chrom)
            if sig in seen:
                continue
            seen.add(sig)
            population.append(chrom)
        while len(population) < pop_size:
            population.append(list(base))
        return population

    def _score_population(
        self,
        problem: PackingProblem,
        jobs: list[PieceJob],
        population: list[list[int]],
        deadline: float,
    ) -> tuple[list[tuple[list[int], Fitness, PackingSolution]], bool]:
        scored: list[tuple[list[int], Fitness, PackingSolution]] = []
        timed_out = False
        for chrom in population:
            if time.perf_counter() >= deadline:
                timed_out = True
                break
            ordered_jobs = [jobs[idx] for idx in chrom]
            solution = self._decoder.solve(problem, ordered_jobs)
            scored.append((chrom, _fitness_tuple(solution), solution))
        return scored, timed_out

    def _tournament_select(
        self,
        scored: list[tuple[list[int], Fitness, PackingSolution]],
        tournament_size: int,
        rng: random.Random,
    ) -> list[int]:
        best = scored[rng.randrange(len(scored))][0]
        for _ in range(tournament_size - 1):
            candidate = scored[rng.randrange(len(scored))][0]
            if self._chrom_better(candidate, best, scored):
                best = candidate
        return list(best)

    def _chrom_better(
        self,
        a: list[int],
        b: list[int],
        scored: list[tuple[list[int], Fitness, PackingSolution]],
    ) -> bool:
        lookup = {tuple(ch): fit for ch, fit, _ in scored}
        return _fitness_better(lookup[tuple(a)], lookup[tuple(b)])

    def _order_crossover(
        self, parent_a: list[int], parent_b: list[int], rng: random.Random
    ) -> list[int]:
        n = len(parent_a)
        i, j = sorted((rng.randrange(n), rng.randrange(n)))
        if i == j:
            return list(parent_a)

        child: list[int | None] = [None] * n
        child[i : j + 1] = parent_a[i : j + 1]
        used = set(parent_a[i : j + 1])

        fill_vals = [g for g in parent_b if g not in used]
        fill_idx = 0
        for k in range(n):
            if child[k] is None:
                child[k] = fill_vals[fill_idx]
                fill_idx += 1
        return [int(g) for g in child]

    def _mutate(self, chrom: list[int], mutation_rate: float, rng: random.Random) -> None:
        if len(chrom) < 2 or rng.random() >= mutation_rate:
            return
        i, j = sorted((rng.randrange(len(chrom)), rng.randrange(len(chrom))))
        if i == j:
            return
        if rng.random() < 0.5:
            chrom[i], chrom[j] = chrom[j], chrom[i]
            return
        gene = chrom.pop(j)
        chrom.insert(i, gene)

    def _fallback_maxrects(self, problem: PackingProblem) -> PackingSolution:
        best: PackingSolution | None = None
        best_fit: Fitness | None = None
        for jobs in job_orderings_for_search(problem.item_types):
            sol = self._decoder.solve(problem, jobs)
            fit = _fitness_tuple(sol)
            if best_fit is None or _fitness_better(fit, best_fit):
                best = sol
                best_fit = fit
        return best if best is not None else self._decoder.solve(problem, [])
