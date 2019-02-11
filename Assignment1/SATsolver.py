import itertools as it
import numpy as np


def SATsolver(sud_input, rules_input):
    '''
    This function takes as input the DIMACS format of a sudoku and the DIMACS format of the sudoku rules to correctly
    Solve a sudoku
    '''

    # TODO read the rules
    problem = []
    nr_variables = ""
    nr_rules = ""
    with open(rules_input, 'r') as f:
        lines = f.read().splitlines()

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


    # TODO GENERALIZE

    variables = list(set(abs(var) for clause in problem for var in clause))
    data = {'true': [], 'false': [], 'unk': []}

    # set all variables to unknown
    for var in variables:
        data['unk'].append(var)


    '''
    var_count = '999'

    var_values = {}

    # dit moet gegeneraliseerd:
    
    for i in range(int(var_count[0])):
        for j in range(int(var_count[1])):
            for h in range(int(var_count[2])):
                print(i+1,j+1,h+1)


    for i in range(len(var_count)):
        for j in range(int(var_count[i])):
            print(i+1, j+1)

    # Get all combinations of [1, 2, 3]
    # and length 2
    comb = it.permutations(range(1, 10), len(var_count))
    print(len(list(comb)))

    count = 0
    for p in it.product(range(int(var_count[0])), repeat=len(var_count)):
        print(p)
        count += 1

    print(count)
    '''

    # TODO GENERALIZE

    with open(sud_input, 'r') as f:
        lines = f.read().splitlines()

        print(lines)

        for line in lines:

            rule = line.split()
            del rule[-1]

            for var in rule:
                data['true'].append(int(var))

    print(data)
    # TODO solve

    # keep track of count to prevent infinite loop
    count = 0
    while len(problem) > 0 and count < 1:
        count += 1
        # step 1, simplify using initial sudoku
        pass
        # step 2, simplify using rules

        # step 3, split if necessary

        # step 4, rinse and repeat

    return


SATsolver("output.txt", "sudoku-rules.txt")
