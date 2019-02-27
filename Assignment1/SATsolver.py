import copy
import random
import sys
import numpy as np

from Heuristics import MOM_function, JW_function, x_wing, y_wing

import globals

import time

def main():


    # if len(sys.argv) != 2:
    #     sys.stdout.write("Usage: SAT -Sn inputfile\n " #TODO geef juiste Usage info
    #                      "*n = 1 for DP\n*n = 2 for MOM\n*n = 3 for JW *n = 4 for x-wing\n*n = 5 for y-wing")
    #     sys.exit(1)
    #TODO make code run with commandline


    globals.initialize()

    startTime = time.time()

    SATsolver("output.txt", "sudoku-rules.txt")
    print('The script took {0} seconds!'.format(time.time() - startTime))

def SATsolver(sud_input, rules_input):

    # get the problem
    problem, variables = read_rules(rules_input)

    # keep track of variable assignments
    data = {'true': set(), 'false': set()}

    # eliminate the known variable from the problem
    problem, data = eliminate_known_vars(problem, data, sud_input)

    # filter tautologies from problem
    problem = filter_tautologies(problem) ### TODO sudokos do not contain tautologies so this needs to be tested

    # solve
    SAT = solve_with_recursion(problem, data, variables)

    if SAT == False:
        sys.stdout.write("This problem is unsatisfiable.")

    else:
        print("SOLVED") # DEBUG


def solve_with_recursion(problem, data, variables):
    """
    Simplify and split. If empty clause then backtrack and reassign.
    Until a) the problem is satisfied (write solution to solution.txt in DIMACS format) and return True
          b) it is clear that the problem is unsatisfiable (return False)
    :param problem: A list of clauses to solve.
    :param data: Dictionary storing assignments of variables.
    :return: bool (True if the problem is satisfied, False if the problem is unsatisfiable).
    """

    # first check for x-wing heuristic
    #problem, data, nr_x_wings, nr_x_removed = x_wing(problem, data)


    #globals.experiment_data['x-wings'] += nr_x_wings
    #globals.experiment_data['x-removed'] += nr_x_removed


    # check for y-wing heuristic
    #problem, data, nr_y_wings, nr_y_removed = y_wing(problem, data)


    #globals.experiment_data['y-wings'] += nr_y_wings
    #globals.experiment_data['y-removed'] += nr_y_removed


    # simplification
    problem, data = simplify_clauses(problem, data, variables)

    globals.experiment_data['clauses'].append(len(problem))

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>LENGTH", len(problem)) # DEBUG

    if contains_empty_clause(problem):
        return False # UNSATISFIED

    if problem == []:
        # then the current assignments are a solution to this problem

        print("This the solution", data) # DEBUG

        write_solution_to_DIMACS_file(data)

        return True # SATISFIED

    # split
    new_problem, new_data, variable, var_assignment = split(problem, data, variables)


    globals.experiment_data['splits'] += 1

    SAT = solve_with_recursion(new_problem, new_data, variables)

    if SAT:
        return True
    else:
        print("backtrack") # DEBUG

        globals.experiment_data['backtracks'] += 1

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

        return solve_with_recursion(new_problem, new_data, variables)


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

def split(problem, data, variables):
    """
    Randomly assigns an yet unassigned variable in the problem to True or False
    :param problem: The current problem which is a list of clauses.
    :param data: Dictionary storing assignments of variables.
    :return: new_problem, new_data, variable (the variable picked during this split),
        var_assignment (the assignment of the variable in during split).
    """
    print("SPLIT") # DEBUG

    # pick randomly a variable that still occurs in the current problem
    variable = abs(random.choice(random.choice(problem)))

    # and randomly assign a value (true or false) to this variable
    var_assignment = bool(random.getrandbits(1))

    ##############
    # Heuristics #
    ##############

    #variable, var_assignment = MOM_function(problem, 4)

    variable, var_assignment = JW_function(problem)

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

    variables = list(set(abs(var) for clause in problem for var in clause))

    return problem, variables

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

            known_var_assignment = line.split()

            # get rid of the DIMACS 0
            del known_var_assignment[-1]

            known_var_assignment = int(known_var_assignment[0])

    # for known_var_assignment in [118, 233, 327, 246, 359, 372, 425, 467, 554, 565, 577, 641, 683, 731, 786, 798, 838, 845, 881, 929, 974]:

            variable = abs(known_var_assignment)

            # a minus sign means "not", therefore the variable needs to be assigned to false if negative number
            if known_var_assignment < 0:
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


def simplify_clauses(problem, data, variables):

    # to keep track of pure literals
    pure_literal_dict = {}

    # indicates if the problem can still be simplified
    simplifiable = True

    # experiment data
    nr_unit_clauses = 0
    nr_pure_literals = 0

    # simplify until problem is solved or problem cannot longer be simplified
    while len(problem) > 0 and simplifiable:

        simplifiable = False

        ###############################################
        # step 1, simplify using true/false variables #
        ###############################################

        new_problem = []

        for clause in problem:
            new_clause = list(np.copy(clause))

            clause_satisfied = False
            for literal in clause:

                if abs(literal) in data['true']:

                    # check if it is a negative, remove the literal if it is a negative
                    if literal < 0:
                        # remove literal from clause, don't use INDEX!
                        new_clause.remove(literal)
                        simplifiable = True

                    # remove the clause if literal within is true
                    else:
                        clause_satisfied = True
                        simplifiable = True

                elif abs(literal) in data['false']:
                    # check if it is a positive, remove the literal if it is a positive
                    if literal > 0:
                        new_clause.remove(literal)
                        simplifiable = True

                    # remove the clause if literal within is false
                    else:
                        clause_satisfied = True
                        simplifiable = True

            # append new clause to new problem
            if not clause_satisfied:
                new_problem.append(new_clause)

        # save changed problem
        problem = new_problem

        ################################
        # step 2, simplify using rules #
        ################################

        # reset dictionary
        for var in variables:
            pure_literal_dict[var] = {"pos": 0, "neg": 0}


        # loop through problem
        for i, clause in enumerate(problem):

            ##############################
            # unit clause simplification #
            ##############################

            if len(clause) == 1:
                nr_unit_clauses += 1

                var = problem[i][0]

                # if the variable is positive, it has to be true in order for the clause to be true
                if var > 0:
                    if abs(var) not in data['false']:
                        data['true'].add(abs(var))
                # and vice versa
                else:
                    if abs(var) not in data['true']:
                        data['false'].add(abs(var))


            ###############################
            # Tautology and pure literals #
            ###############################

            for literal in clause:

                # keep track of positive and negative occurences of literals to find pure literals
                if literal > 0:
                    pure_literal_dict[abs(literal)]["pos"] += 1

                elif literal < 0:
                    pure_literal_dict[abs(literal)]["neg"] += 1

        # loop through the pure literal dict to find whether we have pure literals
        for literal in pure_literal_dict:

            pos = pure_literal_dict[literal]["pos"]
            neg = pure_literal_dict[literal]["neg"]

            # check whether one of them is equal to 0:
            # if there are no positives, set the literal to false
            if pos == 0 and pos != neg:
                if literal not in data['true']:
                    data['false'].add(literal)
                    simplifiable = True

                    # experiment data
                    nr_pure_literals += 1

            # if there are no negatives, set the literal to true
            elif neg == 0 and pos != neg:
                if literal not in data['false']:
                    data['true'].add(literal)
                    simplifiable = True

                    # experiment data
                    nr_pure_literals += 1

    # TODO save this in the while loop or after everything is done??

    globals.experiment_data['pures'].append(nr_pure_literals)
    globals.experiment_data['units'].append(nr_unit_clauses)

    return problem, data

if __name__ == '__main__':
    main()
