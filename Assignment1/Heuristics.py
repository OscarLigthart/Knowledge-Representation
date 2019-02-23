import numpy as np
import random
import itertools

def JW_function(problem):

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

def literal_subset(data, variables):
    """
    Use human strategy to create a subset of literals
    :param data: literals with known true/false values
    :param variables: all literals in the problem
    :return: subset of literals to choose from
    """

    # create dictionary keeping count of variables
    num = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}

    # get all last values in the known variables (last value represents the number on the board)
    for literal in data['true']:
        num[int(str(abs(literal))[2])] += 1

    subset = []

    while True:
        # get max count, return all literals holding that variable
        mx_tuple = max(num.items(), key=lambda x: x[1])
        max_list = [i[0] for i in num.items() if i[1] == mx_tuple[1]]
        number = random.choice(max_list)

        # loop through all variables
        for literal in variables:
            # check if variable is unknown
            if literal not in data['true'] and literal not in data['false']:
                # check if variable holds final number
                if int(str(abs(literal))[2]) == number:
                    subset.append(literal)

        # problem: if there are no unknown values holding that number, what to do?
        if len(subset) == 0:
            # remove this number from the dict and retry loop
            del num[number]
        else:
            break

    return subset

def human_strategy(data, variables):

    subset = literal_subset(data, variables)
    print(subset)

    print(len(variables) - len(data['true']) - len(data['false']))

    # pick a random from the subset? or use heuristic, start with random
    literal = random.choice(subset)

    var_assignment = bool(random.getrandbits(1))

    return literal, var_assignment





def MOM_function(problem, k):

    # [f(x) + f(x')]*2^k + f(x) * f(x')

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

def x_wing(problem, data):
    """This function performs the x-wing strategy (heuristic) on the current sudoku board"""

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
                #indices = np.where(first_coord == i)
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

            # print("found a row x-wing for the value of: " + str(key))
            # print("in the following columns:")
            # print(row_x_wing)
            # print("for the rows:")
            # print(r)

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
                            data['false'].add(literal)

        # if there is an item in col_x_wing, set all other rows holding the value to false
        if col_x_wing:

            # print("found a col x-wing for the value of: " + str(key))
            # print("in the following rows:")
            # print(col_x_wing)
            # print("for the columns:")
            # print(c)

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
                            # set this literal to false
                            data['false'].add(literal)

    return problem, data





