import itertools as it


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


    # TODO create dictionary with all variables

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




    # TODO read the sudoku input and alter variables

    # TODO solve

    # simplify using rules

    # split if necessary

    # rinse and repeat

    return


SATsolver("output.txt", "sudoku-rules.txt")
