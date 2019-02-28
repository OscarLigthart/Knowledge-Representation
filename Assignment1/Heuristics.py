import numpy as np
import random
import itertools


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

    # two sided MOM?
    if MOM.get(literal, 0) >= MOM.get(-literal, 0):
        var_assignment = True
    else:
        var_assignment = False

    return literal, var_assignment

def naked_pairs(problem, data):

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
                            #print(starting_row)
                            starting_col = int((col1_pair1-1)/3)
                            #print(starting_col)
                            for i in range((starting_row*3)+1, (starting_row*3)+4):
                                for j in range((starting_col*3)+1, (starting_col*3)+4):
                                    for h in range(2):
                                        # convert to the variable value
                                        literal = 100 * i + 10 * j + int(str(pair[h])[2])

                                        if literal not in data['true'] and literal not in data['false'] and \
                                                literal not in pair and literal not in pair2:
                                            data['false'].add(literal)
                                            nr_removed += 1

    return problem, data, nr_removed, nr_pairs

def naked_triples(problem, data):

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
                    # now we have a naked triple, what's next?
                    # remove all unknowns that occur in the same row
                    for i in range(1,10):
                        for value in uniques:
                            if i not in cols:
                                literal = (100*key + 10*i + value)
                                if literal not in data['true'] and literal not in data['false']:
                                    data['false'].add(literal)
                                    nr_removed += 1
                                    #print(literal)

            # there should be as many different 2 length clauses as there are 2 length clauses

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

    # extract the values?
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
                    # now we have a naked triple, what's next?
                    # remove all unknowns that occur in the same row
                    for i in range(1, 10):
                        for value in uniques:
                            if i not in rows:
                                literal = (100 * i + 10 * key + value)
                                if literal not in data['true'] and literal not in data['false']:
                                    data['false'].add(literal)
                                    nr_removed += 1
                                    #print(literal)

    ##############################
    # Naked triples in the BOXES #
    ##############################

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

    # now for each value,
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
                # sla in beide de i op?
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

            if abs(row_x_wing[0][0] - row_x_wing[0][1]) < 3 and abs(r[0] - r[1]) < 3:
                continue

            # # print(unknowns)
            # print("found a row x-wing for the value of: " + str(key))
            # print("in the following columns:")
            # print(row_x_wing)
            # print("for the rows:")
            # print(r)

            # check if not in the same box? --> for this, either one has to have at least a difference of 3
            #if abs(row_x_wing[0][0] - row_x_wing[0][1]) < 3 or abs(r[0] - r[1]) < 3:
            #    continue

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

            print('new x wing')
            print(row_x_wing)

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
                        print(coords)
                        if (var_row, var_col) not in coords:
                            if literal not in data['false'] and literal not in data['true']:
                                data['false'].add(literal)
                                all_removed.add(literal)
                                print(literal)

            nr_removed = len(all_removed)

            # update problem


            return problem, data, nr_x_wings, nr_removed, all_removed

        # if there is an item in col_x_wing, set all other rows holding the value to false
        if col_x_wing:

            # print("found a col x-wing for the value of: " + str(key))
            # print("in the following rows:")
            # print(col_x_wing)
            # print("for the columns:")
            # print(c)

            # create combinations of the remainders to check whether they reside in the same boxes
            #if int((check[0][1] - 1) / 3) == int((check[1][1] - 1) / 3) == int((check[2][1] - 1) / 3) and \
            #        int((check[0][0] - 1) / 3) == int((check[1][0] - 1) / 3) == int((check[2][0] - 1) / 3):
            # the rows are within col_x_wing
            # the columns are within c

            if abs(col_x_wing[0][0] - col_x_wing[0][1]) < 3 and abs(c[0] - c[1]) < 3:
                continue

            # make the coordinate combinations and use modulo on all of them, check if they are not the same
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

            print('x-wing found')
            print(col_x_wing)
            list(col_x_wing[0])
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
                            print(coords)
                            if literal not in data['false'] and literal not in data['true']:
                                # set this literal to false
                                data['false'].add(literal)
                                all_removed.add(literal)
                                print(literal)

            nr_removed = len(all_removed)
            return problem, data, nr_x_wings, nr_removed, all_removed

    # check the amount of literals set to false
    nr_removed = len(all_removed)

    return problem, data, nr_x_wings, nr_removed, all_removed

def y_wing(problem, data):
    """
    This function recognizes the y-wing pattern in a sudoku and changes
    the values of the literals according to the y-wing heuristic/strategy
    """

    nr_y_wings = 0
    all_removed = set()

    # STEP 1: Look for doubles in unknowns
    unknowns = set()
    # get all unknown variables
    for clause in problem:
        for literal in clause:
            unknowns.add(abs(literal))

    # initiate doubles dictionary
    doubles = {}


    # double in the values, for each coordinate set, check if there exist only 2 values
    for row in range(1,10):
        for col in range(1,10):
            doubles[(row, col)] = []
            for value in range(1,10):
                # convert possibility into literal
                lit = 100*row + 10*col + value

                # check if possible literal exists in unknowns, keep count if it does for every coordinate
                if lit in unknowns:
                    doubles[(row, col)].append(lit)

    double_coordinates = []
    double_values = []

    # scan dictionary for doubles
    for key, value in doubles.items():
        if len(value) == 2:
            # save coordinates (to check for overlap)
            double_coordinates.append(key)
            double_values.append(tuple([int(str(value[0])[2]),
                                       int(str(value[1])[2])]))

    # now we have a nested list of all the doubles in the sudoku
    # look for the pivot and pincer values
    # find the first 3 indices
    y_wings = set()

    count = 0

    all_coordinates = set()

    # loop through double values
    for h, double in enumerate(double_values):
        # loop through the actual single values
        for i, value in enumerate(double):
            # compare these to the remaining double values
            for k, double2 in enumerate(double_values):
                if double == double2:
                    continue

                for j, value2 in enumerate(double2):
                    count += 1
                    if value2 == value:
                        # what now?
                        # save other values of double and see if there is a double in the list holding them both
                        other_values = tuple(sorted([double[1 - i], double2[1 - j]]))

                        if other_values in double_values:
                            # save potential y_wing
                            y_wings.add(tuple(sorted((double, double2, other_values))))

                            # get coordinates of first and second double, along with final other
                            # values
                            # for all occurrences of the other value, append the list
                            indices = [i for i, x in enumerate(double_values) if x == other_values]

                            for l in indices:
                                all_coordinates.add(tuple(sorted([double_coordinates[h],
                                                                  double_coordinates[k],
                                                                  double_coordinates[l]])))

    # after having found the possible y-wing configurations, we check whether
    # the final constraints are met. Here we extract the pivot and pincers.
    for coordinates in all_coordinates:
        for coordinate in coordinates:
            # find the coordinate that conflicts with both to get the pivot
            conflicts = set()
            r = coordinate[0]
            c = coordinate[1]
            # for the remaining coordinates: see if there exists a conflict
            for coordinate2 in coordinates:
                if coordinate2 == coordinate:
                    continue

                # check for row
                if coordinate2[0] == r:
                    # conflict with one
                    conflicts.add(coordinate2)

                # check for column
                if coordinate2[1] == c:
                    # conflict with one
                    conflicts.add(coordinate2)

                # check for same box
                # how? row and column must be within modulo 3
                if int((coordinate2[0] - 1) / 3) == int((r - 1) / 3) and int((coordinate2[1] - 1) / 3) == int((c - 1) / 3):
                    conflicts.add(coordinate2)

            # found the pivot! Now check the overlapping value of the other doubles
            if len(conflicts) == 2:

                # check if the points do not all lie on the same row or column
                extract_conflicts = list(conflicts)
                check = [coordinate, extract_conflicts[0], extract_conflicts[1]]
                if check[0][1] == check[1][1] == check[2][1] or \
                        check[0][0] == check[1][0] == check[2][0]:
                    continue

                # and check if not all the points are in the same box
                if int((check[0][1] - 1) / 3) == int((check[1][1] - 1) / 3) == int((check[2][1] - 1) / 3) and \
                    int((check[0][0] - 1) / 3) == int((check[1][0] - 1) / 3) == int((check[2][0] - 1) / 3):
                    continue

                both_double = []
                for double_coord in conflicts:
                    # find the index in the coordinate list to find the double it belongs to
                    index = double_coordinates.index(double_coord)
                    both_double.append(double_values[index])

                    # check!
                    # now for these doubles, use the coordinates to find literal values
                    # of overlapping variables, they can be removed

                value = [val for val in both_double[0] if val in both_double[1]][0]

                conflicts = list(conflicts)
                coord1 = conflicts[0]
                coord2 = conflicts[1]

                remove_unknowns = set()

                # get all coordinates for overlapping rows
                # loop over board again? --> see if a coordinate conflicts with both
                for row in range(1, 10):
                    for col in range(1, 10):

                        row_conflict_1 = False
                        col_conflict_1 = False
                        box_conflict_1 = False
                        row_conflict_2 = False
                        col_conflict_2 = False
                        box_conflict_2 = False

                        # the coordinate needs to be conflicting with both coordinates,
                        # in order to check for this we keep track of the conflicts of the
                        # individual coordinates and see if these conflicts combined also occur
                        if coord1[0] == row:
                            row_conflict_1 = True

                        if coord1[1] == col:
                            col_conflict_1 = True

                        if int((coord1[0] - 1) / 3) == int((row - 1) / 3) and int((coord1[1] - 1) / 3) == int(
                                (col - 1) / 3):
                            box_conflict_1 = True

                        if coord2[0] == row:
                            row_conflict_2 = True

                        if coord2[1] == col:
                            col_conflict_2 = True

                        if int((coord2[0] - 1) / 3) == int((row - 1) / 3) and int((coord2[1] - 1) / 3) == int(
                                (col - 1) / 3):
                            box_conflict_2 = True

                        if (row_conflict_1 and col_conflict_2) or (row_conflict_1 and box_conflict_2) or \
                                (col_conflict_1 and row_conflict_2) or (col_conflict_1 and box_conflict_2) or \
                                (box_conflict_1 and row_conflict_2) or (box_conflict_1 and col_conflict_2):
                            # append the coordinate along with the value to the list of unknowns
                            remove_unknowns.add(100 * row + 10 * col + value)

                # now we remove the pivot point from the remove_unknowns and we adjust the data
                remove_unknowns.remove(100 * coordinate[0] + 10 * coordinate[1] + value)

                # for all these unknowns, we check if they can be set to false
                for variable in remove_unknowns:
                    if variable in unknowns:
                        if variable not in data['false'] and variable not in data['true']:
                            data['false'].add(variable)
                            all_removed.add(variable)

                # keep track of the amount of y-wings found
                nr_y_wings += 1

    # keep track of the amount of literals that can be removed using this strategy
    nr_removed = len(all_removed)

    return problem, data, nr_y_wings, nr_removed


def show(sudoku):
    for i, line in enumerate(sudoku):
        for j, char in enumerate(line):
            if j % 3 == 0 and j != 0:
                print('  ', end="")
                if char == 0:
                    print('_', end=" ")
                else:
                    print(int(char), end=" ")
            else:
                if char == 0:
                    print('_', end=" ")
                else:
                    print(int(char), end=" ")

        if (i + 1) % 3 == 0 and i != 0:
            print('\n')

        else:
            print('')


