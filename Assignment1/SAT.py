import argparse
from SATsolver import *
import globals

def main():

    # failsafe, to check if user inserted correct input
    if ARGS.sudoku_files == None:
        raise ImportError("Please insert a .txt file that consists of a concatenation of the sudoku-rules \
                          and the sudoku in DIMACS format (in that order)")

    # check for heuristic input
    if ARGS.heuristic == "S1":
        print("Running DP algorithm.")
    elif ARGS.heuristic == "S2":
        print("Running DP algorithm with JW heuristic.")
    elif ARGS.heuristic == "S3":
        print("Running DP algorithm with MOM heuristic.")
    else:
        raise ImportError("Please insert any of these options to run a heuristic: S1, S2, S3")

    # check for strategy input
    if ARGS.strategy == "naked-pairs":
        print("Using naked-pairs human strategy.")
    elif ARGS.strategy == "naked-triples":
        print("Using naked-triples human strategy.")
    elif ARGS.strategy == "x-wings":
        print("Using x-wing human strategy.")
    elif ARGS.strategy == "all":
        print("Using all human strategies.")
    elif ARGS.strategy == None:
        pass
    else:
        raise ImportError("Please insert any of these options to run a human-strategy: naked-pairs, naked-triples, \
                           x-wings, all")

    globals.initialize()
    SATsolver(None, ARGS.sudoku_files, ARGS)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sudoku_files', default=None, type=str,
                        help='Concatenation of sudoku and the rules')
    parser.add_argument('--heuristic', default="S1", type=str,
                        help='Used to specify which heuristic to use')
    parser.add_argument('--strategy', default=None, type =str,
                        help='Used to specify which strategy to use')

    ARGS = parser.parse_args()

    main()
