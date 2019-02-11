
def SATsolver(sud_input, rules_input):
    '''
    This function takes as input the DIMACS format of a sudoku and the DIMACS format of the sudoku rules to correctly
    Solve a sudoku
    '''

    # TODO read the rules

    with open(rules_input, 'r') as f:
        lines = f.read().splitlines()
        print(lines)

        # for each word in the line:
        for line in lines:
            # print the word
            vars = line.split()
            print(vars)

        f.close()


    # TODO create dictionary with all variables

    # TODO read the sudoku input and alter variables

    # TODO solve

    # simplify using rules

    # split if necessary

    # rinse and repeat

    return


SATsolver("output.txt", "sudoku-rules.txt")
