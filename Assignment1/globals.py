def initialize():
    global experiment_data
    experiment_data = {'level': "", "sudoku_nr": 0,
                       'splits': 0, 'backtracks': 0,
                       'nr-naked-pairs': 0,
                       'naked-pairs-removed': 0,
                       'naked-triples-removed': 0,
                       'nr-naked-triples': 0,
                       'x-wings': 0, 'x-removed': 0,
                       'y-wings': 0, 'y-removed': 0,
                       'runtime': 0,
                       'clauses': [], 'pures': [], 'units': []
                       ,"shown": False}