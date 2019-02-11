import numpy as np

# step 1, convert 1 sudoku to SAT format

def sud2sat(sudoku_file):
    # read sudoku file (only start with the first line)
    with open(sudoku_file, 'r') as f:
        lines = f.read().splitlines()

        f.close()

    sudoku = np.zeros((9,9))
    # set clausules
    # for i in range(len(lines)):
    # TODO: make this work for all sudoku's in the text file
    for i in range(1):
        # initiate full list of sudoku DIMACS variables
        rules = ""
        lines[i]
        sud = list(lines[i])

        # loop through sudoku notation
        for j, num in enumerate(sud):
            # check if a number is present in a cell
            if num != '.':
                # convert to integer and get appropriate coordinates
                num = int(num)
                row, col = divmod(j, 9)
                sudoku[row, col] = num

                # get DIMACS variable
                DIMval = str(100*(row+1) + 10*(col+1) + num)

                rules += (DIMval + " 0" + '\n')

    # write DIMACS file
    f = open("output.txt", "w")
    f.write(rules)
    f.close()

    return sudoku

sud2sat("1000 sudokus.txt")