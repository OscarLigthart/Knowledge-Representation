import pickle
from SATsolver import SATsolver
from Heuristics import MOM_function, JW_function, x_wing, y_wing

import time
import globals

NR_REPLICATES = 1 # set the number of replicates
METHOD = "JW-y-wing"


def main():


    sudoku_files = {"simple": "sudokus/50_simple_sudokus.txt",
                    "easy": "sudokus/50_easy_sudokus.txt",
                    "intermediate": "sudokus/50_intermediate_sudokus.txt",
                    "expert": "sudokus/50_expert_sudokus.txt"}

    # UNCOMMENT FOR TEST
    #sudoku_files = {"expert": "sudokus/50_expert_sudokus.txt"}
    #sudoku_files = {"intermediate": "sudokus/50_intermediate_sudokus.txt"}


    for level, sudoku_file_path in sudoku_files.items():

        collected_data = []

        # determine number of sudokus in file (always 50 in this case)
        with open(sudoku_file_path, 'r') as sudokus_file:
            number_of_sudokus = len(sudokus_file.read().splitlines())


        # UNCOMMENT FOR TEST
        #number_of_sudokus = 5

        # go over each sudoku in the current file
        for sudoku_nr in range(number_of_sudokus):
            print(sudoku_nr, level)

            # write current sudoku from .txt file in DIMACS format
            sud2sat_experiments(sudoku_file_path, sudoku_nr)

            # run the SAT solver on the current sudoku for the give number of replicates
            replicates = []
            for i in range(NR_REPLICATES):

                # create new data storage
                globals.initialize()
                globals.experiment_data["level"] = level
                globals.experiment_data["sudoku_nr"] = sudoku_nr

                startTime = time.time()
                SATsolver("sudoku_DIMACS_format.txt", "sudoku-rules.txt")

                # store runtime
                globals.experiment_data["runtime"] = time.time() - startTime

                #print(globals.experiment_data) # DEBUG

                replicates.append(globals.experiment_data)

            collected_data.append(replicates)

        data_filename = METHOD + "_" + level

        pickle.dump(collected_data, open("data/" + data_filename + ".p", "wb"))



def sud2sat_experiments(sudoku_file, sudoku_nr):

    sudoku_file = open(sudoku_file, 'r')
    sudokus = sudoku_file.read().splitlines()

    DIMACS_file = open('sudoku_DIMACS_format.txt', 'w')
    DIMACS_file.truncate(0)  # clears the sudoku_DIMACS_format.txt file

    # pick the sudoku on its line number
    sudoku = sudokus[sudoku_nr]

    for i, entry in enumerate(sudoku):
        if entry != '.':
            # determine the row and column number of the current entry
            row_of_entry, col_of_entry = divmod(i, 9)

            # encode the current entry in DIMACS format
            DIMACS = str(row_of_entry + 1) + str(col_of_entry + 1) + entry + " 0"

            DIMACS_file.write(DIMACS + "\n") #TODO make sure no newline after last write

    sudoku_file.close()
    DIMACS_file.close()


if __name__ == '__main__':
    main()