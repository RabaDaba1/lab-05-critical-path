from ..model import Project
from ..project_network import ProjectNetwork
from ...simplex.model import Model
from ...simplex.expressions.expression import Expression
from ..solution import BasicSolution


class Solver:
    '''
    Simplex based solver looking for the critical path in the project.
    Uses linear model maximizing length of the path in the project network. 

    Attributes:
    ----------
    project_network: ProjectNetwork
        a project network related to the given project
    model: simplex.model.Model
        a linear model looking for the maximal path in the project network
    Methods:
    --------
    __init__(problem: Project)
        create a solver for the given project
    create_model() -> simplex.model.Model
        builds a linear model of the problem
    solve() -> BasicSolution
        finds the duration of the critical (longest) path in the project network
    '''
    def __init__(self, problem: Project):
        self.project_network = ProjectNetwork(problem)
        self.model = self.create_model()

    def create_model(self) -> Model:
        # TODO:
        # 0) we need as many variables as there are edges in the project network
        # 1) every variable has to be <= 1
        # 2) sum of the variables starting at the initial state has to be equal 1
        # 3) sum of the variables ending at the goal state has to be equal 1
        # 4) for every other node, total flow going trough it has to be equal 0
        #    i.e. sum of incoming arcs minus sum of the outgoing arcs = 0
        # 5) we have to maximize length of the path
        #    (sum of variables weighted by the durations of the corresponding tasks)
        #
        # tip 1. `self.project_network` is the project network you should use
        #        - read documentation of ProjectNetwork class in 
        #          `saport/critical_path/project_network.py` for guidance
        model = Model("critical path (max)")
        
        start_node = self.project_network.start_node
        goal_node = self.project_network.goal_node

        # 0) For each edge in a project create a variable
        edges = self.project_network.edges()

        variables = {edge: model.create_variable(f'variable_{i}') for i, edge in enumerate(edges)}

        # 1) Set constraints so that every variable is <= 1
        for edge in edges:
            model.add_constraint(Expression(variables[edge]) <= 1)


        # 2) Add constraint to variables starting at an initial state
        successors_variables = [
            Expression(
                variables[(start_node, succ, self.project_network.arc_task(start_node, succ))]
            )
            for succ in self.project_network.successors(start_node)
        ]
        model.add_constraint(var_sum(successors_variables) == 1)

        # 3) Add constraint to variables ending at a goal state
        predecessors_variables = [
            Expression(
                variables[(pred, goal_node, self.project_network.arc_task(pred, goal_node))]
            )
            for pred in self.project_network.predecessors(goal_node)
        ]
        model.add_constraint(var_sum(predecessors_variables) == 1)

        # 4) Set flow going through other variables equal to 1
        for node in self.project_network.nodes():
            if node != start_node and node != goal_node:
                incoming = [(pred, node, self.project_network.arc_task(pred, node)) for pred in self.project_network.predecessors(node)]
                exiting = [(node, succ, self.project_network.arc_task(node, succ)) for succ in self.project_network.successors(node)]

                exiting_sum = var_sum([Expression(variables[edge]) for edge in exiting])
                incoming_sum = var_sum([Expression(variables[edge]) for edge in incoming])

                model.add_constraint(exiting_sum - incoming_sum == 0)

        
        # 5) Set models objecitve to path's length maximization
        path_length = var_sum([Expression(variables[edge]) * edge[2].duration for edge in edges])
        model.maximize(path_length)

        return model

    def solve(self) -> BasicSolution:
        solution = self.model.solve()
        return BasicSolution(int(solution.objective_value()))
