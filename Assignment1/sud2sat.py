import numpy as np

#
# def sud2sat_experiments(sudoku_file):
#     # read sudoku file (only start with the first line)
#     sudoku_file = open(sudoku_file, 'r')
#     sudokus = sudoku_file.read().splitlines()
#
#     DIMACS_file = open('all_sudokus_DIMACS_format.txt', 'w')
#     DIMACS_file.truncate(0)  # clears the all_sudokus_DIMACS_format.txt file
#
#     for sudoku in sudokus:
#         DIMACS_file.write("start\n")
#         for i, entry in enumerate(sudoku):
#             if entry != '.':
#
#                 # determine the row and column number of the current entry
#                 row_of_entry, col_of_entry = divmod(i, 9)
#
#                 # encode the current entry in DIMACS format
#                 DIMACS = str(row_of_entry + 1) + str(col_of_entry + 1) + entry + " 0"
#
#                 DIMACS_file.write(DIMACS + "\n")
#         DIMACS_file.write("end\n")
#
#
#     sudoku_file.close()
#     DIMACS_file.close()


#
# def sud2sat(sudoku_file):
#     # read sudoku file (only start with the first line)
#     sudoku_file = open(sudoku_file, 'r')
#     sudokus = sudoku_file.read().splitlines()
#
#     DIMACS_file = open('output_2.txt', 'w')
#     DIMACS_file.truncate(0)  # clears the solution.txt file
#
#
#     for sudoku in sudokus:
#         for i, entry in enumerate(sudoku):
#             if entry != '.':
#
#                 # determine the row and column number of the current entry
#                 row_of_entry, col_of_entry = divmod(i, 9)
#
#                 # encode the current entry in DIMACS format
#                 DIMACS = str(row_of_entry + 1) + str(col_of_entry + 1) + entry + " 0"
#
#                 DIMACS_file.write(DIMACS + "\n")
#
#     sudoku_file.close()
#     DIMACS_file.close()


# sud2sat_experiments("1000 sudokus.txt")






# CODE OSCAR

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