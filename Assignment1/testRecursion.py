import copy
import random

def main():
    SAT = SATsolver("output.txt", "sudoku-rules.txt")
    print(SAT)

def SATsolver(sud_input, rules_input):

    # get the problem
    problem = read_rules(rules_input)

    # keep track of variable assignments
    data = {'true': set(), 'false': set()}

    # elimate the known variable from the problem
    problem, data = eliminate_known_vars(problem, data, sud_input)

    # filter tautologies from problem
    problem = filter_tautologies(problem) ### TODO sudokos do not contain tautologies so this needs to be tested

    print("length of current problem ", len(problem))

    # problem = [[1, -2], [1, -3, 2], [3, 2, -1], [-2, -1, 3],[4, -1]] # test problem

    # solve
    SAT = solve_with_recursion(problem, data) # solve_with_tree()

    if SAT == False:
        print("This problem does not have a solution")

    return SAT


def update_problem(problem, variable, var_assignment):
    """
        updates the problem after variable is set to a certain value
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
    updated_data = copy.deepcopy(data)
    if var_assignment == True:
        updated_data["true"].add(variable)
    elif var_assignment == False:
        updated_data["false"].add(variable)

    return updated_data


def solve_with_recursion(problem, data):

    # simplify using unit clauses and pure literals
    problem, data = filter_unit_clauses(problem, data)

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>LENGTH", len(problem))


    if contains_empty_clause(problem):
        # print("BACKTRACK")
        return False # unsatisfied

    if problem == []:
        # then the current assignments is the solution to this problem
        print("This the solution", data) # output
        return True # satisfied

    # print("current problem", problem)
    # print("current data", data)

    # split
    new_problem, new_data, variable, var_assignment = split(problem, data)

    # print("new var", variable)
    # print("new data", new_data)
    # print("new problem", new_problem)

    SAT = solve_with_recursion(new_problem, new_data)

    if SAT:
        # print("solved")
        return True
    else:

        print("backtrack")

        # print("this variable was", variable, var_assignment)

        # reassign variable
        # if it was true
        if var_assignment == True:

            # make it now false
            var_assignment = False

        # if it was false
        elif var_assignment == False:

            # make it now true
            var_assignment = True

        # print("and is now", variable, var_assignment)

        # now this variable has a value assigned, the problem will change: so update the problem
        new_problem = update_problem(problem, variable, var_assignment)

        # remember the value we assigned to this variable by storing it in the data
        new_data = update_data(data, variable, var_assignment)

        # print("new data", new_data)
        # print("new problem", new_problem)


        return solve_with_recursion(new_problem, new_data)


def split(problem, data):

    # pick randomly a variable that still occurs in the current problem
    variable = abs(random.choice(random.choice(problem)))

    # and randomly assign a value (true or false) to this variable
    var_assignment = bool(random.getrandbits(1))

    # remember the value we assigned to this variable by storing it in the data
    updated_data = update_data(data, variable, var_assignment)

    # now this variable has a value assigned, the problem will change: so update the problem
    updated_problem = update_problem(problem, variable, var_assignment)

    return updated_problem, updated_data, variable, var_assignment


def contains_empty_clause(problem):
    empty_clause = False
    for clause in problem:
        if clause == []:
            empty_clause = True

    return empty_clause


def read_rules(rules_input):

    problem = []
    nr_variables = ""
    nr_rules = ""
    with open(rules_input, 'r') as f:
        lines = f.read().splitlines() #TODO generalize

        firstline = True

        # for each word in the line:
        for line in lines:

            if firstline:
                info = line.split()
                nr_variables = info[2]
                nr_rules = info[3]
                firstline = False
                continue

            rule = line.split()

            del rule[-1]

            rule = [int(i) for i in rule]

            problem.append(rule)

    return problem

def eliminate_known_vars(problem, data, sud_input):
    with open(sud_input, 'r') as f:
        lines = f.read().splitlines()

        for line in lines:

            known_var_assigment = line.split()

            del known_var_assigment[-1]

            known_var_assigment = int(known_var_assigment[0])

            variable = abs(known_var_assigment)

            if known_var_assigment < 0:
                var_assignment = False
            else:
                var_assignment = True

            problem = update_problem(problem, variable, var_assignment)

            data = update_data(data, variable, var_assignment)

    return problem, data

def filter_tautologies(problem):

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
    unit_clause_in_problem = True
    # pure_literal_in_problem = True

    print("START FILTER UNIT CLAUSE")

    while (problem != [] and unit_clause_in_problem):

        print(len(problem))

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

                unit_clause_in_problem = True
                break

    return problem, data


if __name__ == '__main__':
    main()



