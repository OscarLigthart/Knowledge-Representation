import copy
import random
import sys
from Tree import *

import time

def main():
    startTime = time.time()
    SATsolver("output.txt", "sudoku-rules.txt")
    print('The script took {0} seconds!'.format(time.time() - startTime))

def SATsolver(sud_input, rules_input):

    # get the problem
    problem = read_rules(rules_input)

    # keep track of variable assignments
    data = {'true': set(), 'false': set()}

    # eliminate the known variable from the problem
    problem, data = eliminate_known_vars(problem, data, sud_input)

    # filter tautologies from problem
    problem = filter_tautologies(problem) ### TODO sudokos do not contain tautologies so this needs to be tested

    # problem = [[1, -2], [1, -3, 2], [3, 2, -1], [-2, -1, 3],[4, -1]] # DEBUG
    # print("length of current problem ", len(problem)) # DEBUG

    # solve
    # UNCOMMENT THE METHOD TO USE
    SAT = solve_with_recursion(problem, data)
    # SAT = solve_with_tree(problem, data)

    if SAT == False:
        sys.stdout.write("This problem is unsatisfiable.")

    else:
        print("SOLVED")


def solve_with_recursion(problem, data):
    """
    Simplify and split. If empty clause then backtrack and reassign.
    Until a) the problem is satisfied (write solution to solution.txt in DIMACS format) and return True
          b) it is clear that the problem is unsatisfiable (return False)
    :param problem: A list of clauses to solve.
    :param data: Dictionary storing assignments of variables.
    :return: bool (True if the problem is satisfied, False if the problem is unsatisfiable).
    """

    # simplify problem by filtering unit clauses
    problem, data = filter_unit_clauses(problem, data)

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>LENGTH", len(problem)) # DEBUG

    if contains_empty_clause(problem):
        return False # UNSATISFIED

    if problem == []:
        # then the current assignments are a solution to this problem

        print("This the solution", data) # DEBUG

        write_solution_to_DIMACS_file(data)

        return True # SATISFIED

    # split
    new_problem, new_data, variable, var_assignment = split(problem, data)

    SAT = solve_with_recursion(new_problem, new_data)

    if SAT:
        return True
    else:
        print("backtrack") # DEBUG

        # reassign variable:
        # if it was true make it now false
        if var_assignment == True:
            var_assignment = False
        # if it was false make it now true
        elif var_assignment == False:
            var_assignment = True

        # now this variable has a value assigned, the problem will change: so update the problem
        new_problem = update_problem(problem, variable, var_assignment)

        # remember the value we assigned to this variable by storing it in the data
        new_data = update_data(data, variable, var_assignment)

        return solve_with_recursion(new_problem, new_data)


def solve_with_tree(problem, data):
    # initialize the tree
    tree = Tree(problem, data)

    # continue reducing the problem until we find either a solution to this problem (aka empty problem list) or we find that there
    # is no solution to this problem (aka problem is not satisfiable)

    SAT = True
    while (tree.current_node.problem != [] and SAT):

        empty_clause = False
        while (True):

            # and update the current node in the tree after filtering unit clauses
            tree.current_node.problem, tree.current_node.data = filter_unit_clauses(tree.current_node.problem, tree.current_node.data)

            if tree.current_node.problem == []:
                break

            empty_clause = contains_empty_clause(tree.current_node.problem)
            if empty_clause:
                break

            tree.split_tree()

        if empty_clause:
            SAT = tree.backtrack()

    if SAT == True:
        write_solution_to_DIMACS_file(tree.current_node.data)

    return SAT


def update_problem(problem, variable, var_assignment):
    """
    Updates the problem after a variable got a new assignment
    :param problem: The current problem, which is a list of clauses, that needs to be updated.
    :param variable: The variable that got an assignment
    :param var_assignment: The assignment (either True of False) the variable got.
    :return: new_problem (problem updated as result of the new assignment)
    """

    new_problem = []

    for clause in problem:
        new_clause = copy.deepcopy(clause)
        clause_satisfied = False
        for literal in clause:

            # if the variable appears in the clause
            if abs(literal) == variable:

                # if the variable appears as a neg. literal
                if literal < 0:
                    # and the variable is assigned to true, the outcome will be "not" true -> so false
                    if var_assignment == True:
                        # in that case the literal needs to be removed from the clause
                        new_clause.remove(literal)

                    # however, if the variable is assigned to false, the outcome will be "not" false -> so true
                    elif var_assignment == False:
                        # in that case the clause is satisfied
                        clause_satisfied = True
                # if the variable appears as a pos. literal
                else:

                    # and the variable is assigned to true, the outcome will be true
                    if var_assignment == True:
                        # in that case the clause is satisfied
                        clause_satisfied = True

                    # however, if the variable is assigned to false, the outcome will be false
                    if var_assignment == False:
                        # in that case the literal needs to be removed from the clause
                        new_clause.remove(literal)

        # if the clause is not satisfied, it will remain in the problem
        if not clause_satisfied:
            new_problem.append(new_clause)

    return new_problem


def update_data(data, variable, var_assignment):
    """
    Updates the dictionary that stores the assignments of variables given a variable and its assignment.
    :param data: Dictionary storing assignments of variables that needs to be updated.
    :param variable: The variable that got an assignment.
    :param var_assignment: The assignment (either True or False) the variable got.
    :return: updated_data.
    """

    new_data = copy.deepcopy(data)
    if var_assignment == True:
        new_data["true"].add(variable)
    elif var_assignment == False:
        new_data["false"].add(variable)

    return new_data

def split(problem, data):
    """
    Randomly assigns an yet unassigned variable in the problem to True or False
    :param problem: The current problem which is a list of clauses.
    :param data: Dictionary storing assignments of variables.
    :return: new_problem, new_data, variable (the variable picked during this split),
        var_assignment (the assignment of the variable in during split).
    """
    print("SPLIT")
    # pick randomly a variable that still occurs in the current problem
    variable = abs(random.choice(random.choice(problem)))

    # and randomly assign a value (true or false) to this variable
    var_assignment = bool(random.getrandbits(1))

    # remember the value we assigned to this variable by storing it in the data
    new_data = update_data(data, variable, var_assignment)

    # now this variable has a value assigned, the problem will change: so update the problem
    new_problem = update_problem(problem, variable, var_assignment)

    return new_problem, new_data, variable, var_assignment


def contains_empty_clause(problem):
    """
    Determines if the problem contains an empty clause.

    :param problem: The current problem which is a list of clauses.
    :return: empty_clause (bool indicating if there is an empty clause).

    """

    empty_clause = False
    for clause in problem:
        if clause == []:
            empty_clause = True

    return empty_clause


def write_solution_to_DIMACS_file(data):
    # write solution to DIMACS file
    solution_file = open('solution.txt', 'w')
    solution_file.truncate(0)  # clears the solution.txt file


    # DEBUG: UNCOMMENT THIS IN ORDER TO TEST IF SOLUTION FROM solution.txt FILE IS CORRECT
    # for i, var in enumerate(data["false"]):
    #     solution_file.write("-"+str(var) + " 0\n")
    #

    for i, var in enumerate(data["true"]):
        solution_file.write(str(var) + " 0")

        # no enter after last line
        if i != len(data["true"]) - 1:
            solution_file.write("\n")

    solution_file.close()

def read_rules(rules_input):
    """
    Takes a DIMACS file containing rules and transforms it into a set of clauses that needs to be solved
    :param rules_input: The name of the DIMACS file containing rules
    :return: problem (list of clauses to solve)
    """

    problem = []
    with open(rules_input, 'r') as f:
        lines = f.read().splitlines() #TODO generalize

        firstline = True

        # for each word in the line:
        for line in lines:
            # skip first line
            if firstline:
                firstline = False
                continue

            rule = line.split()

            # get rid of the DIMACS 0
            del rule[-1]

            # build the problem
            clause = [int(i) for i in rule]
            problem.append(clause)

    return problem

def eliminate_known_vars(problem, data, sud_input):
    """
    Takes a DIMACS file with variables which are already given in the problem and assigns those variables accordingly.
    :param problem: The current problem which is a list of clauses.
    :param data: Dictionary storing assignments of variables.
    :param sud_input: The name of the DIMACS file containing known variables.
    :return: problem (updated problem), data (updated data).
    """

    with open(sud_input, 'r') as f:
        lines = f.read().splitlines()

        for line in lines:

            known_var_assigment = line.split()

            # get rid of the DIMACS 0
            del known_var_assigment[-1]

            known_var_assigment = int(known_var_assigment[0])

            variable = abs(known_var_assigment)

            # a minus sign means "not", therefore the variable needs to be assigned to false if negative number
            if known_var_assigment < 0:
                var_assignment = False
            else:
                var_assignment = True

            # update problem with this new assignment
            problem = update_problem(problem, variable, var_assignment)

            # keep track of the assignments
            data = update_data(data, variable, var_assignment)


    #  DEBUG: UNCOMMENT THIS IN ORDER TO TEST IF SOLUTION FROM solution.txt FILE IS CORRECT
    # with open("solution.txt", 'r') as f:
    #     lines = f.read().splitlines()
    #
    #     for line in lines:
    #
    #         known_var_assigment = line.split()
    #
    #         # get rid of the DIMACS 0
    #         del known_var_assigment[-1]
    #
    #         known_var_assigment = int(known_var_assigment[0])
    #
    #         variable = abs(known_var_assigment)
    #
    #         # a minus sign means "not", therefore the variable needs to be assigned to false if negative number
    #         if known_var_assigment < 0:
    #             var_assignment = False
    #         else:
    #             var_assignment = True
    #
    #         # update problem with this new assignment
    #         problem = update_problem(problem, variable, var_assignment)
    #
    #         # keep track of the assignments
    #         data = update_data(data, variable, var_assignment)
    #
    #     print("AFTER kNOWN", len(problem))
    #     print(problem)

    return problem, data

def filter_tautologies(problem):
    """
    Filters tautologies from the problem and returns this simplified problem.
    :param problem: The current problem which is a list of clauses.
    :return: new_problem (problem without tautologies).
    """
    new_problem = []

    # detect if there is a tautology
    for clause in problem:
        new_clause = copy.deepcopy(clause)

        clause_satisfied = False
        for literal in clause:

            # if the counter part of a literal is within the clause, there exists a tautology
            if (literal * - 1) in clause:
                # so clause will always be satisfied
                clause_satisfied = True

        # only keep the unsatisfied clauses
        if not clause_satisfied:
            new_problem.append(new_clause)

    return new_problem


def filter_unit_clauses(problem, data):
    """
    Filters unit clauses from the problem and returns this simplified problem.
    :param problem: The current problem which is a list of clauses.
    :param data: Dictionary storing assignments of variables.
    :return: problem (without unit clauses), data (updated data).
    """

    # there might be unit clauses
    unit_clause_in_problem = True

    print("START FILTER UNIT CLAUSE") # DEBUG

    # filter unit clauses until there are no more unit clauses or the problem is solved
    while (unit_clause_in_problem and problem != []):

        print(len(problem)) # DEBUG

        # if we do not find unit clauses in this cycle, then there are no unit clauses
        unit_clause_in_problem = False

        for clause in problem:

            # a unit clause only contains one literal
            if len(clause) == 1:

                literal = clause[0]

                variable = abs(literal)

                # if the literal is negative, the variable needs to be assigned to false, because "not"False = True
                if literal < 0:
                    var_assignment = False

                # else the variable needs to be assigned to true
                else:
                    var_assignment = True

                # update the problem
                problem = update_problem(problem, variable, var_assignment)

                # keep track of the assignments
                data = update_data(data, variable, var_assignment)

                # we found a unit clause, so there might be more of them
                unit_clause_in_problem = True
                break

    return problem, data


if __name__ == '__main__':
    main()
