"""
This script is responsible for the concatenation of the Sudoku game state
in DIMACS format and the Sudoku rules in DIMACS format
"""

filenames = ['sudoku-rules.txt', 'sudoku_DIMACS_format.txt']
with open('concatenated-sudoku.txt', 'w') as outfile:
    for fname in filenames:
        with open(fname) as infile:
            for line in infile:
                outfile.write(line)
