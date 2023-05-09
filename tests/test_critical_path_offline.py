from copy import deepcopy, copy
from pathlib import Path

import pytest

from saport.critical_path.model import Project
from saport.critical_path.project_network import ProjectState
from saport.critical_path.solution import FullSolution
from saport.critical_path.solvers.cpm_solver import Solver as CpmSolver
from saport.critical_path.solvers.simplex_solver_max import Solver as SimplexMaxSolver
from saport.critical_path.solvers.simplex_solver_min import Solver as SimplexMinSolver
from saport.simplex.expressions.objective import ObjectiveType

TEST_DIR = "example_input"

def indented_string(s: str, ident: str = '    '):
    return '\n' + '\n'.join([ident + l for l in s.splitlines()])

def pretty_state(s):
    if len(s.done) == 0:
        return "{}"
    else:
        return str(set(s.done))

def pretty_times(times):
    return "{" + ", ".join([f"{pretty_state(s)}: {t}" for s,t in times.items()]) + "}"

def expand_case(path: str):
    path = Path(TEST_DIR).joinpath(path)
    return Project.from_file(path), FullSolution.expected_solution_from_file(path)

class TestSimplexSolvers:

    @pytest.mark.parametrize("case", [
        "project_01.txt",
        "project_02.txt",
        "project_03.txt"
    ])
    def test_simplex_should_solve_problem_by_minimization(
        self, case
    ):
        project, correct_solution = expand_case(case)     
        solver = SimplexMinSolver(project)

        assert (
            solver.model.objective.type == ObjectiveType.MIN
        ), "objective is not `min`:" +\
            f"\n- got model: {indented_string(str(solver.model))}" +\
            f"\n- for project: {case}"  
        
        solution = solver.solve()
        assert (
            solution.duration == correct_solution.duration
        ), "found critical path is incorrect:" +\
            f"\n- got duration: {solution.duration}" +\
            f"\n- expected: {correct_solution.duration}" +\
            f"\n- using model: {indented_string(str(solver.model))}" +\
            f"\n- for project: {case}"  

    @pytest.mark.parametrize("case", [
        "project_01.txt",
        "project_02.txt",
        "project_03.txt",
    ])
    def test_simplex_should_solve_problem_by_maximization(
        self, case
    ):
        project, correct_solution = expand_case(case)     
        solver = SimplexMaxSolver(project)

        assert (
            solver.model.objective.type == ObjectiveType.MAX
        ), "objective is not `max`:" +\
            f"\n- got model: {indented_string(str(solver.model))}" +\
            f"\n- for project: {case}"  
        
        solution = solver.solve()
        assert (
            solution.duration == correct_solution.duration
        ), "found critical path is incorrect:" +\
            f"\n- got duration: {solution.duration}" +\
            f"\n- expected: {correct_solution.duration}" +\
            f"\n- using model: {indented_string(str(solver.model))}" +\
            f"\n- for project: {case}"  


class TestCpmSolver:
    
    @pytest.mark.parametrize("case, exp_times", [
        ('project_01.txt', {ProjectState(index=1, done=frozenset()): 0, ProjectState(index=2, done=frozenset({'A'})): 4, ProjectState(index=3, done=frozenset({'B', 'A'})): 4, ProjectState(index=4, done=frozenset({'B', 'A', 'D', 'E', 'C'})): 9, ProjectState(index=5, done=frozenset({'A', 'E', 'D', 'B', 'C', 'F'})): 11}),
        ('project_03.txt', {ProjectState(index=1, done=frozenset()): 0, ProjectState(index=2, done=frozenset({'A'})): 10, ProjectState(index=3, done=frozenset({'B'})): 10, ProjectState(index=4, done=frozenset({'C', 'A'})): 30, ProjectState(index=5, done=frozenset({'D', 'B', 'C', 'A'})): 30, ProjectState(index=6, done=frozenset({'A', 'E', 'D', 'B', 'C', 'F'})): 40}),
        ('project_02.txt', {ProjectState(index=1, done=frozenset()): 0, ProjectState(index=2, done=frozenset({'A'})): 5, ProjectState(index=3, done=frozenset({'B', 'A'})): 15, ProjectState(index=4, done=frozenset({'D', 'B', 'A'})): 29, ProjectState(index=5, done=frozenset({'B', 'F', 'A'})): 23, ProjectState(index=6, done=frozenset({'A', 'D', 'E', 'G', 'B', 'C', 'F'})): 41, ProjectState(index=7, done=frozenset({'H', 'A', 'D', 'E', 'G', 'B', 'C', 'F'})): 45, ProjectState(index=8, done=frozenset({'H', 'A', 'D', 'E', 'I', 'G', 'B', 'C', 'F'})): 59, ProjectState(index=9, done=frozenset({'H', 'A', 'E', 'D', 'I', 'G', 'B', 'J', 'C', 'F'})): 64})
    ])
    def test_should_propagate_times_forward_for_each_state(
        self, case, exp_times
    ):
        project, _ = expand_case(case)     
        solver = CpmSolver(project)
        got_times = solver.forward_propagation()

        assert (
            got_times == exp_times
        ), "the forward propagation returned incorrect result:" +\
            f"\n- got times: {pretty_times(got_times)}" +\
            f"\n- expected: {pretty_times(exp_times)}" +\
            f"\n- for project: {case}"  


    @pytest.mark.parametrize("case, earliest_times, exp_times", [
        ('project_01.txt', {ProjectState(index=1, done=frozenset()): 0, ProjectState(index=2, done=frozenset({'A'})): 4, ProjectState(index=3, done=frozenset({'A', 'B'})): 4, ProjectState(index=4, done=frozenset({'A', 'C', 'D', 'E', 'B'})): 9, ProjectState(index=5, done=frozenset({'D', 'E', 'B', 'A', 'C', 'F'})): 11}, {ProjectState(index=5, done=frozenset({'D', 'E', 'B', 'A', 'C', 'F'})): 11, ProjectState(index=4, done=frozenset({'A', 'C', 'D', 'E', 'B'})): 9, ProjectState(index=3, done=frozenset({'A', 'B'})): 6, ProjectState(index=2, done=frozenset({'A'})): 4, ProjectState(index=1, done=frozenset()): 0}),
        ('project_03.txt', {ProjectState(index=1, done=frozenset()): 0, ProjectState(index=2, done=frozenset({'A'})): 10, ProjectState(index=3, done=frozenset({'B'})): 10, ProjectState(index=4, done=frozenset({'A', 'C'})): 30, ProjectState(index=5, done=frozenset({'A', 'C', 'B', 'D'})): 30, ProjectState(index=6, done=frozenset({'D', 'E', 'B', 'A', 'C', 'F'})): 40}, {ProjectState(index=6, done=frozenset({'D', 'E', 'B', 'A', 'C', 'F'})): 40, ProjectState(index=5, done=frozenset({'A', 'C', 'B', 'D'})): 30, ProjectState(index=4, done=frozenset({'A', 'C'})): 30, ProjectState(index=2, done=frozenset({'A'})): 10, ProjectState(index=3, done=frozenset({'B'})): 10, ProjectState(index=1, done=frozenset()): 0}),
        ('project_02.txt', {ProjectState(index=1, done=frozenset()): 0, ProjectState(index=2, done=frozenset({'A'})): 5, ProjectState(index=3, done=frozenset({'A', 'B'})): 15, ProjectState(index=4, done=frozenset({'A', 'B', 'D'})): 29, ProjectState(index=5, done=frozenset({'A', 'F', 'B'})): 23, ProjectState(index=6, done=frozenset({'D', 'E', 'G', 'B', 'A', 'C', 'F'})): 41, ProjectState(index=7, done=frozenset({'D', 'E', 'G', 'H', 'B', 'A', 'C', 'F'})): 45, ProjectState(index=8, done=frozenset({'D', 'E', 'I', 'G', 'H', 'B', 'A', 'C', 'F'})): 59, ProjectState(index=9, done=frozenset({'D', 'E', 'G', 'I', 'H', 'B', 'A', 'C', 'F', 'J'})): 64}, {ProjectState(index=9, done=frozenset({'D', 'E', 'G', 'I', 'H', 'B', 'A', 'C', 'F', 'J'})): 64, ProjectState(index=8, done=frozenset({'D', 'E', 'I', 'G', 'H', 'B', 'A', 'C', 'F'})): 59, ProjectState(index=7, done=frozenset({'D', 'E', 'G', 'H', 'B', 'A', 'C', 'F'})): 45, ProjectState(index=6, done=frozenset({'D', 'E', 'G', 'B', 'A', 'C', 'F'})): 41, ProjectState(index=4, done=frozenset({'A', 'B', 'D'})): 29, ProjectState(index=5, done=frozenset({'A', 'F', 'B'})): 31, ProjectState(index=3, done=frozenset({'A', 'B'})): 15, ProjectState(index=2, done=frozenset({'A'})): 5, ProjectState(index=1, done=frozenset()): 0})
    ])
    def test_should_propagate_times_backward_for_each_state(
        self, case, earliest_times, exp_times
    ):
        project, _ = expand_case(case)     
        solver = CpmSolver(project)
        got_times = solver.backward_propagation(deepcopy(earliest_times))

        assert got_times == exp_times, \
               "the backward propagation returned incorrect result:" +\
              f"\n- got times: {pretty_times(got_times)}" +\
              f"\n- expected: {pretty_times(exp_times)}" +\
              f"\n- given the earliest times: {pretty_times(earliest_times)}" +\
              f"\n- for project: {case}"  

    @pytest.mark.parametrize("case, earliest_times, latest_times, exp_slacks", [
        ('project_01.txt', {ProjectState(index=1, done=frozenset()): 0, ProjectState(index=2, done=frozenset({'A'})): 4, ProjectState(index=3, done=frozenset({'B', 'A'})): 4, ProjectState(index=4, done=frozenset({'B', 'D', 'E', 'C', 'A'})): 9, ProjectState(index=5, done=frozenset({'C', 'A', 'B', 'D', 'E', 'F'})): 11}, {ProjectState(index=5, done=frozenset({'C', 'A', 'B', 'D', 'E', 'F'})): 11, ProjectState(index=4, done=frozenset({'B', 'D', 'E', 'C', 'A'})): 9, ProjectState(index=3, done=frozenset({'B', 'A'})): 6, ProjectState(index=2, done=frozenset({'A'})): 4, ProjectState(index=1, done=frozenset()): 0}, {'A': 0, 'B': 3, 'E': 5, 'D': 0, 'C': 2, 'F': 0}),
        ('project_03.txt', {ProjectState(index=1, done=frozenset()): 0, ProjectState(index=2, done=frozenset({'A'})): 10, ProjectState(index=3, done=frozenset({'B'})): 10, ProjectState(index=4, done=frozenset({'C', 'A'})): 30, ProjectState(index=5, done=frozenset({'C', 'D', 'B', 'A'})): 30, ProjectState(index=6, done=frozenset({'C', 'A', 'B', 'D', 'E', 'F'})): 40}, {ProjectState(index=6, done=frozenset({'C', 'A', 'B', 'D', 'E', 'F'})): 40, ProjectState(index=5, done=frozenset({'C', 'D', 'B', 'A'})): 30, ProjectState(index=4, done=frozenset({'C', 'A'})): 30, ProjectState(index=2, done=frozenset({'A'})): 10, ProjectState(index=3, done=frozenset({'B'})): 10, ProjectState(index=1, done=frozenset()): 0}, {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 5, 'E': 0}),
        ('project_02.txt', {ProjectState(index=1, done=frozenset()): 0, ProjectState(index=2, done=frozenset({'A'})): 5, ProjectState(index=3, done=frozenset({'B', 'A'})): 15, ProjectState(index=4, done=frozenset({'B', 'D', 'A'})): 29, ProjectState(index=5, done=frozenset({'B', 'A', 'F'})): 23, ProjectState(index=6, done=frozenset({'G', 'C', 'A', 'B', 'D', 'E', 'F'})): 41, ProjectState(index=7, done=frozenset({'G', 'C', 'A', 'B', 'D', 'E', 'F', 'H'})): 45, ProjectState(index=8, done=frozenset({'I', 'G', 'C', 'H', 'A', 'B', 'D', 'E', 'F'})): 59, ProjectState(index=9, done=frozenset({'I', 'C', 'G', 'H', 'A', 'B', 'D', 'E', 'J', 'F'})): 64}, {ProjectState(index=9, done=frozenset({'I', 'C', 'G', 'H', 'A', 'B', 'D', 'E', 'J', 'F'})): 64, ProjectState(index=8, done=frozenset({'I', 'G', 'C', 'H', 'A', 'B', 'D', 'E', 'F'})): 59, ProjectState(index=7, done=frozenset({'G', 'C', 'A', 'B', 'D', 'E', 'F', 'H'})): 45, ProjectState(index=6, done=frozenset({'G', 'C', 'A', 'B', 'D', 'E', 'F'})): 41, ProjectState(index=4, done=frozenset({'B', 'D', 'A'})): 29, ProjectState(index=5, done=frozenset({'B', 'A', 'F'})): 31, ProjectState(index=3, done=frozenset({'B', 'A'})): 15, ProjectState(index=2, done=frozenset({'A'})): 5, ProjectState(index=1, done=frozenset()): 0}, {'A': 0, 'B': 0, 'C': 11, 'D': 0, 'F': 8, 'E': 0, 'G': 8, 'H': 0, 'I': 0, 'J': 0})
    ])
    def test_should_properly_create_slacks_based_on_earliest_and_latest_times(
        self, case, earliest_times, latest_times, exp_slacks
    ):
        project, _ = expand_case(case)     
        solver = CpmSolver(project)
        got_slacks = solver.calculate_slacks(deepcopy(earliest_times), deepcopy(latest_times))

        assert got_slacks == exp_slacks, "solver has not found correct slacks:" +\
              f"\n- got slacks: {got_slacks}" +\
              f"\n- expected: {exp_slacks}" +\
              f"\n- given the earliest times: {pretty_times(earliest_times)}" +\
              f"\n- and the latest times: {pretty_times(latest_times)}" +\
              f"\n- for project: {case}" 

    @pytest.mark.parametrize("case, slacks", [
        ('project_01.txt', {'A': 0, 'B': 3, 'E': 5, 'D': 0, 'C': 2, 'F': 0}),
        ('project_03.txt', {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 5, 'E': 0}),
        ('project_02.txt', {'A': 0, 'B': 0, 'C': 11, 'D': 0, 'F': 8, 'E': 0, 'G': 8, 'H': 0, 'I': 0, 'J': 0})
    ])
    def test_should_be_able_to_evaluate_critical_paths(
        self, case, slacks
    ):
        project, correct_solution = expand_case(case)
        solver = CpmSolver(project)
        got_paths = solver.create_critical_paths(copy(slacks))
        exp_paths = correct_solution.critical_paths

        assert sorted(got_paths) == sorted(exp_paths), \
            "solver has not found all correct critical paths:" +\
            f"\n- got paths: {got_paths}" +\
            f"\n- expected paths: {exp_paths}" +\
            f"\n- given the slacks: {slacks}" +\
            f"\n- for project: {case}" 
