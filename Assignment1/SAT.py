import argparse
from SATsolver import *
import globals

def main():

    if ARGS.sudoku_files == None:
        raise ImportError("Please insert a .txt file that consists of a concatenation of the sudoku-rules \
                          and the sudoku in DIMACS format (in that order)")

    # todo maybe build a failsafe for if file is not handed correctly?

    globals.initialize()
    SATsolver(None, ARGS.sudoku_files, ARGS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sudoku_files', default=None, type=str,
                        help='Concatenation of sudoku and the rules')
    parser.add_argument('--heuristic', default="S1", type=str,
                        help='Used to specify which heuristic to use')

    ARGS = parser.parse_args()

    main()
