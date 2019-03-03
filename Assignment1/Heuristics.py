import numpy as np
import random
import itertools
import globals


def JW_function(problem):
    """
    This function applies the two-sided Jeroslang-Wang heuristic to choose an unknown literal
    to split on in a SAT-solver
    :param problem: the problem consisting of all unsatisfied clauses
    :return: literal to split on and the True or False assignment of it
    """
    J = {}
    two_sided_J = {}
    for clause in problem:
        for literal in clause:
            weight = (2 ^ (-len(clause)))
            J[abs(literal)] = J.get(abs(literal), 0) + weight
            two_sided_J[literal] = two_sided_J.get(literal, 0) + weight


    # check for both literals
    absolute_vars = set([abs(x) for x in list(J.keys())])

    literal = max(J, key=J.get)

    # two-sided JW, check which value the literal should take on
    if two_sided_J.get(literal, 0) >= two_sided_J.get(-literal, 0):
        var_assignment = True
    else:
        var_assignment = False

    return literal, var_assignment


def MOM_function(problem, k):
    """
    This function applies the MOM-heuristic in the form of the following function:

     [f(x) + f(x')]*2^k + f(x) * f(x')

    in order to choose the literal to split on in a SAT solver.
    It also counts the occurrences of the literals to decide the boolean value such that
    it satisfies as much clauses as possible
    :param problem: the problem consisting of all unsatisfied clauses
    :param k: parameter to tune MOM
    :return: literal to split on and the True or False assignment of it
    """
    #

    # get all shortest clauses?
    clause_lengths = [len(x) for x in problem]
    min_length = min(clause_lengths)

    # initialize dictionaries
    occurrences = {}
    MOM = {}

    # loop through clauses of minimum length
    for clause in problem:

        if len(clause) == min_length:
            # keep track of occurrences
            for literal in clause:
                occurrences[literal] = occurrences.get(literal, 0) + 1

    absolute_vars = set([abs(x) for x in list(occurrences.keys())])

    for literal in absolute_vars:
        # extract positive and negative counts, if they do not occur in either form, return 0
        pos_counts = occurrences.get(literal, 0)
        neg_counts = occurrences.get(-literal, 0)

        MOM[literal] = ((pos_counts + neg_counts) * 2 ^ k) + (pos_counts * neg_counts)

    # get highest value
    literal = max(MOM, key=MOM.get)

    # two sided MOM
    if MOM.get(literal, 0) >= MOM.get(-literal, 0):
        var_assignment = True
    else:
        var_assignment = False

    return literal, var_assignment

def naked_pairs(problem, data):
    """
    This function identifies the naked-pairs on the sudoku board by looking at the remaining conflict clauses
    :param problem: conflict clauses
    :param data: variable assignments
    :return: conflict clauses, altered variable assignments
    """

    nr_removed = 0
    nr_pairs = 0

    pairs = []
    # loop through problem
    for clause in problem:
        if len(clause) == 2 and clause[0] > 0 and clause[1] > 0:
            # save the possible naked pairs?
            pairs.append(clause)

    # for these pairs, check whether they exist on one line or column? or first check the value?
    for pair in pairs:
        for pair2 in pairs:
            # check if it is not the same pair
            if pair != pair2:
                row1_pair1 = int(str(pair[0])[0])
                row2_pair1 = int(str(pair[1])[0])
                col1_pair1 = int(str(pair[0])[1])
                col2_pair1 = int(str(pair[1])[1])
                val1_pair1 = int(str(pair[0])[2])
                val2_pair1 = int(str(pair[1])[2])

                row1_pair2 = int(str(pair2[0])[0])
                row2_pair2 = int(str(pair2[1])[0])
                col1_pair2 = int(str(pair2[0])[1])
                col2_pair2 = int(str(pair2[1])[1])
                val1_pair2 = int(str(pair2[0])[2])
                val2_pair2 = int(str(pair2[1])[2])

                # check if the coordinates match along the pair
                if row1_pair1 == row2_pair1 and row1_pair2 == row2_pair2 and col1_pair1 == col2_pair1 and \
                    col1_pair2 == col2_pair2:
                    # check if they hold the same values:
                    if (val1_pair1, val2_pair1) == (val1_pair2, val2_pair2):

                        # check if they exist on the same row
                        if row1_pair1 == row1_pair2:
                            nr_pairs += 1
                            # remove the values from this row
                            for i in range(1,10):
                                # convert to the variable value
                                for j in range(2):
                                    literal = 100*int(str(pair[0])[0]) + 10*i + int(str(pair[j])[2])
                                    if literal not in data['true'] and literal not in data['false'] and \
                                            literal not in pair and literal not in pair2:
                                        data['false'].add(literal)
                                        nr_removed += 1

                        # check if they exist on the same column
                        elif col1_pair1 == col1_pair2:
                            nr_pairs += 1
                            # remove the values from these columns
                            for i in range(1, 10):
                                for j in range(2):
                                    # convert to the variable value
                                    literal = 100 * i + 10 * int(str(pair[0])[1]) + int(str(pair[j])[2])

                                    # remove literal if not already assigned a value
                                    if literal not in data['true'] and literal not in data['false'] and \
                                            literal not in pair and literal not in pair2:
                                        data['false'].add(literal)
                                        nr_removed += 1

                        # check if they exist in the same box
                        elif int((row1_pair1-1)/3) == int((row1_pair2-1) / 3) and \
                                int((col1_pair1-1)/3) == int((col1_pair2-1) / 3):

                            nr_pairs += 1

                            # remove the values from this box
                            starting_row = int((row1_pair1-1)/3)
                            starting_col = int((col1_pair1-1)/3)

                            for i in range((starting_row*3)+1, (starting_row*3)+4):
                                for j in range((starting_col*3)+1, (starting_col*3)+4):
                                    for h in range(2):
                                        # convert to the variable value
                                        literal = 100 * i + 10 * j + int(str(pair[h])[2])

                                        # remove literal if not already assigned a value
                                        if literal not in data['true'] and literal not in data['false'] and \
                                                literal not in pair and literal not in pair2:
                                            data['false'].add(literal)
                                            nr_removed += 1

    return problem, data, nr_removed, nr_pairs

def naked_triples(problem, data):
    """
    This function searches for the naked-triple pattern within the remaining conflict clauses and
    safely removes the unknown literals from the problem.
    :param problem: the remaining conflict clauses
    :param data: the truth values assigned to literals
    :return: remaining conflict clauses, altered truth value assignments
    """

    nr_removed = 0
    nr_triple = 0

    #########################################
    # Extract possible naked triple clauses #
    #########################################

    # step 1, identify naked triple --> search whether they have the combination of values in common
    triples = []
    # loop through problem
    for clause in problem:
        if (len(clause) == 2 and clause[0] > 0 and clause[1] > 0) or \
                (len(clause) == 3 and clause[0] > 0 and clause[1] > 0 and clause[2] > 0):

            row_units = []
            col_units = []
            for i in range(len(clause)):
                row_units.append(int(str(clause[i])[0]))
                col_units.append(int(str(clause[i])[1]))

            # if the row and column units are the same across the clause, add them to possible triples
            if len(set(row_units)) == 1 and len(set(col_units)) == 1:
                # save the possible naked pairs?
                triples.append(clause)



    ##################################
    # Look for naked triples in rows #
    ##################################

    row_triples = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}

    # extract the ones that have all rows in common,
    for triple in triples:
        # check for the rows
        row_units = []
        for i in range(len(triple)):
            row_units.append(int(str(triple[i])[0]))

        # cluster the clauses based on the row
        if len(set(row_units)) == 1:
            row_triples[int(str(triple[0])[0])].append(triple)

    # for each of these rows, check whether they share the value according to the
    # naked triples constraint:

    # extract the values?
    # total number of values within this formation must be 3, and the clauses
    # of length 2 have to be different
    for key, clauses in row_triples.items():
        combinations = []
        uniques = set()
        cols = set()
        for clause in clauses:
            comb = []
            for literal in clause:
                comb.append(int(str(literal)[2]))
                uniques.add(int(str(literal)[2]))
                cols.add(int(str(literal)[1]))

            combinations.append(comb)

        # check if the values are shared according to naked triple constraint
        # alo check whether the length 2 clauses are different
        if len(uniques) == 3:
            combo_set = set()
            combo_lis = []
            for combo in combinations:
                if len(combo) == 2:
                    combo_set.add(tuple(combo))
                    combo_lis.append(combo)

            if len(combinations) == 3:
                if len(combo_set) == len(combo_lis):
                    nr_triple += 1
                    # now we have a naked triple, remove all unknowns that occur in the same row
                    for i in range(1,10):
                        for value in uniques:
                            if i not in cols:
                                literal = (100*key + 10*i + value)
                                if literal not in data['true'] and literal not in data['false']:
                                    data['false'].add(literal)

    #####################################
    # Look for naked triples in COLUMNS #
    #####################################

    # now for the columns
    col_triples = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}

    # extract the ones that have all rows in common,
    for triple in triples:
        # check for the columns
        col_units = []
        for i in range(len(triple)):
            col_units.append(int(str(triple[i])[1]))

        # cluster the clauses based on the col
        if len(set(col_units)) == 1:
            col_triples[int(str(triple[0])[1])].append(triple)

    # for each of these rows, check whether they share the value according to the
    # naked triples constraint:

    # total number of values within this formation must be 3, and the clauses
    # of length 2 have to be different
    for key, clauses in col_triples.items():
        combinations = []
        uniques = set()
        rows = set()
        for clause in clauses:
            comb = []
            for literal in clause:
                comb.append(int(str(literal)[2]))
                uniques.add(int(str(literal)[2]))
                rows.add(int(str(literal)[0]))

            combinations.append(comb)

        # check if the values are shared according to naked triple constraint
        # alo check whether the length 2 clauses are different
        if len(uniques) == 3:
            combo_set = set()
            combo_lis = []
            for combo in combinations:
                if len(combo) == 2:
                    combo_set.add(tuple(combo))
                    combo_lis.append(combo)

            if len(combinations) == 3:
                if len(combo_set) == len(combo_lis):
                    nr_triple += 1
                    # now we have a naked triple remove all unknowns that occur in the same row
                    for i in range(1, 10):
                        for value in uniques:
                            if i not in rows:
                                literal = (100 * i + 10 * key + value)
                                if literal not in data['true'] and literal not in data['false']:
                                    data['false'].add(literal)
                                    nr_removed += 1

    return problem, data, nr_removed, nr_triple

def x_wing(problem, data):
    """This function performs the x-wing strategy (heuristic) on the current sudoku board"""

    all_removed = set()
    nr_x_wings = 0

    unknowns = set()
    # get all unknown variables
    for clause in problem:
        for literal in clause:
            unknowns.add(abs(literal))

    num = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}

    # get the coordinates of all the unknown values, structured under the corresponding value
    for literal in unknowns:
        num[int(str(abs(literal))[2])].append((int(str(abs(literal))[0]), int(str(abs(literal))[1])))

    ###################
    # FIND RECTANGLES #
    ###################

    # now for each value, save the row and column coordinate
    for key, value in num.items():
        first_coord = []
        sec_coord = []

        for coordinates in value:
            # first check if a duplicate occurs within the first coordinates
            # make two lists, one for the first coordinate, one for the second
            first_coord.append(coordinates[0])
            sec_coord.append(coordinates[1])

        col_coord = []
        row_coord = []

        col_elements = []
        row_elements = []

        #####################################
        # CHECK IF X-WING CONSTRAINTS APPLY #
        #####################################

        # now count every number within these lists
        for i in range(1, 10):
            if first_coord.count(i) == 2:
                # now check for these coordinates, whether the other coordinates correspond
                # find the index where the coordinates are i and check the other list for same index
                row_coord.append(i)

                indices = [j for j, x in enumerate(first_coord) if x == i]

                # get elements from second coordinates
                elems = [sec_coord[j] for j in indices]

                # save the elements for every key
                col_elements.append(tuple(elems))

            if sec_coord.count(i) == 2:
                # save possible candidate value to the col coordinate list
                col_coord.append(i)

                # now check for these coordinates, whether the other coordinates correspond
                indices = [j for j, x in enumerate(sec_coord) if x == i]

                # get elements from first coordinates
                elems = [first_coord[j] for j in indices]

                # save the elements for every key
                row_elements.append(tuple(elems))

        #############################
        # GET COORDINATES OF X-WING #
        #############################

        # extract the row x-wings and get the coordinates of the x-wing
        new_list = sorted(set(col_elements))
        row_x_wing = []
        r = []
        coords = []

        for i in range(len(new_list)):
            if col_elements.count(new_list[i]) == 2:
                row_x_wing.append(new_list[i])
                indices = [j for j, x in enumerate(col_elements) if x == new_list[i]]
                r = [row_coord[j] for j in indices]

        if r:
            coordinates = itertools.product(r, list(row_x_wing[0]))
            coords = list(coordinates)

        # extract the column x-wings and get the coordinates of the x-wing
        new_list = sorted(set(row_elements))
        col_x_wing = []
        c = []

        for i in range(len(new_list)):
            if row_elements.count(new_list[i]) == 2:
                col_x_wing.append(new_list[i])
                indices = [j for j, x in enumerate(row_elements) if x == new_list[i]]
                c = [col_coord[j] for j in indices]

        if c:
            coordinates = itertools.product(list(col_x_wing[0]), c)
            coords = list(coordinates)


        #############################################
        # ALTER VARIABLE VALUES ACCORDING TO X-WING #
        #############################################

        # check both lists, if there is an item in row_x_wing, set all other columns holding the value to false
        if row_x_wing:

            # check if they appear in different 3x3 boxes
            list_1 = row_x_wing[0]
            list_2 = r
            co_list = []
            co_list2 = []
            for a in itertools.product(list_1, list_2):
                co_list.append((int((a[0] - 1) / 3), int((a[1] - 1) / 3)))
                co_list2.append(a)

            if len(set(co_list)) != len(co_list):
                continue

            # keep track of number of x-wings found
            nr_x_wings += 1

            # search for the values in the column, without altering the current coordinates
            for col in list(row_x_wing[0]):
                for literal in unknowns:
                    # extract literal information
                    var_row = int(str(literal)[0])
                    var_col = int(str(literal)[1])
                    var_val = int(str(literal)[2])
                    # check whether literal is in same column and of the same value
                    if var_col == col and var_val == key:
                        # check whether this literal is not in the x-wing
                        if (var_row, var_col) not in coords:
                            if literal not in list(data['false']) and literal not in list(data['true']):

                                data['false'].add(literal)
                                all_removed.add(literal)

        # if there is an item in col_x_wing, set all other rows holding the value to false
        if col_x_wing:

            # make the coordinate combinations and use modulo on all of them, check if they are not in the same boxes
            list_1 = col_x_wing[0]
            list_2 = c
            co_list = []
            co_list2 = []
            for a in itertools.product(list_1, list_2):
                co_list.append((int((a[0] - 1) / 3), int((a[1] - 1) / 3)))
                co_list2.append(a)

            if len(set(co_list)) != len(co_list):
                continue

            # keep track of number of x-wings found
            nr_x_wings += 1

            # search for the values in the row, without altering the current coordinates
            for row in list(col_x_wing[0]):
                for literal in unknowns:
                    # extract literal information
                    var_row = int(str(literal)[0])
                    var_col = int(str(literal)[1])
                    var_val = int(str(literal)[2])

                    # check whether literal is in same column and of the same value
                    if var_row == row and var_val == key:
                         # check whether this literal is not in the x-wing
                        if (var_row, var_col) not in coords:
                            # if literal not in data['false']:
                            #     print('not in false')
                            #
                            # if literal in data['false']:
                            #     print('in false')
                            if literal not in list(data['false']) and literal not in list(data['true']):

                                # set this literal to false
                                data['false'].add(literal)
                                all_removed.add(literal)
                                if col_x_wing == [(9, 3)]:
                                    print(literal)

    # check the amount of literals set to false
    nr_removed = len(all_removed)

    return problem, data, nr_x_wings, nr_removed, all_removed



