import itertools as it
import numpy as np
import random
import time


def unit_clause_simplification(problem, data, it):
    """
    This function performs a unit clause simplification

    :param problem: total list of left clauses
    :param data: all variables and the value they represent
    :param it: the index of the current clause

    :return:
    """

    var = problem[it][0]

    try:
        data['unk'].remove(abs(var))
    except:
        pass

    # if the variable is positive, it has to be true in order for the clause to be true
    if var > 0:
        data['true'].append(abs(var))
    # and vice versa
    else:
        data['false'].append(abs(var))

    return data

def simplify_clauses(problem, data, variables):

    # initialize dictionary
    pure_literal_dict = {}

    # initialize variable to indicate whether the problem can still be simplified
    simplifiable = True

    count = 0
    # loop while the problem still shows some changes
    while len(problem) > 0 and simplifiable:

        simplifiable = False
        ###############################################
        # step 1, simplify using true/false variables #
        ###############################################

        new_problem = []

        for i, clause in enumerate(problem):
            new_clause = list(np.copy(clause))

            remove = False
            for j, literal in enumerate(clause):

                # TODO check if right elements are deleted
                if abs(literal) in data['true']:

                    # check if it is a negative, remove the literal if it is a negative
                    # TODO create function for this
                    if literal < 0:
                        # remove literal from clause, don't use INDEX!
                        new_clause.remove(literal)
                        simplifiable = True

                    # remove the clause if literal within is true
                    else:
                        remove = True
                        simplifiable = True

                elif abs(literal) in data['false']:
                    # check if it is a positive, remove the literal if it is a positive
                    if literal > 0:
                        new_clause.remove(literal)
                        simplifiable = True

                    # remove the clause if literal within is false
                    else:
                        remove = True
                        simplifiable = True

            # append new clause to new problem
            if not remove:
                new_problem.append(new_clause)

        # save changed problem
        problem = new_problem


        ################################
        # step 2, simplify using rules #
        ################################

        # reset dictionary
        for var in variables:
            pure_literal_dict[var] = {"pos": 0, "neg": 0}

        # keep track of what the new problem will hold
        new_problem = []

        # loop through problem
        for i, clause in enumerate(problem):

            ##############################
            # unit clause simplification #
            ##############################

            if len(clause) == 1:
                data = unit_clause_simplification(problem, data, i)

            ###############################
            # Tautology and pure literals #
            ###############################

            taut = False
            for literal in clause:
                # if the counter part of a literal is within the clause, there exists a tautology
                if (literal * - 1) in clause:
                    taut = True
                    simplifiable = True

                # keep track of positive and negative occurences of literals to find pure literals
                if literal > 0:
                    pure_literal_dict[abs(literal)]["pos"] += 1

                elif literal < 0:
                    pure_literal_dict[abs(literal)]["neg"] += 1

            if not taut:
                new_problem.append(clause)

        problem = new_problem

        # loop through the pure literal dict to find whether we have pure literals
        for literal in pure_literal_dict:

            pos = pure_literal_dict[literal]["pos"]
            neg = pure_literal_dict[literal]["neg"]

            # check whether one of them is equal to 0:
            # if there are no positives, set the literal to false
            if pos == 0 and pos != neg:
                data['false'].append(literal)
                try:
                    data['unk'].remove(literal)
                except:
                    pass

                simplifiable = True

            # if there are no negatives, set the literal to true
            elif neg == 0 and pos != neg:
                data['true'].append(literal)
                try:
                    data['unk'].remove(literal)
                except:
                    pass

                simplifiable = True

        data['false'] = list(set(data['false']))
        data['true'] = list(set(data['true']))

    return problem, data


def SATsolver(sud_input, rules_input):
    '''
    This function takes as input the DIMACS format of a sudoku and the DIMACS format of the sudoku rules to correctly
    Solve a sudoku
    '''

    # TODO might have to change this into one file

    #####################
    # Read sudoku rules #
    #####################

    problem = []

    with open(rules_input, 'r') as f:
        lines = f.read().splitlines()

        firstline = True

        # for each word in the line:
        for line in lines:

            if firstline:
                firstline = False
                continue

            # convert string holding rules to list of literals (clause)
            rule = line.split()
            del rule[-1]
            rule = [int(i) for i in rule]

            # insert the clause into the problem
            problem.append(rule)

    #####################
    # Extract variables #
    #####################

    variables = list(set(abs(var) for clause in problem for var in clause))
    data = {'true': [], 'false': [], 'unk': []}

    # set all variables to unknown
    for var in variables:
        data['unk'].append(var)

    with open(sud_input, 'r') as f:
        lines = f.read().splitlines()

        for line in lines:

            rule = line.split()
            del rule[-1]

            for var in rule:
                data['true'].append(int(var))

    #hardest_sudoku = [118, 233, 327, 246, 359, 372, 425, 467, 554, 565, 577, 641, 683, 731, 786, 798, 838, 845, 881, 929, 974]
    #data['true'] = hardest_sudoku

    ################################
    ####         Solve         #####
    ################################

    # initialize tree dictionary, node, bool_data, dictionary
    tree = {}

    count = 0

    # set the previous literal to be 0 at the start, so we can find the starting point in the tree
    prev_literal = 0

    # keep track of the number of splits
    nr_splits = 0

    while len(problem) > 0:
        count += 1
        ############
        # Simplify #
        ############

        problem, data = simplify_clauses(problem, data, variables)


        # initialize the unknown starting variables
        if count == 1:
            unknown_starts = list(np.copy(data['unk']))


        ######################
        # Split if necessary #
        ######################

        # check if we have an empty clause
        empty = False
        for clause in problem:
            if not clause:
                empty = True

        # check if necessary
        if len(problem) > 0:

            # apply split
            # pick random value from unknowns and set it to either true or false
            if len(data['unk']) > 0 and not empty:

                ###########################
                # choose literal in split #
                ###########################

                # rewrite dictionary with other pointers
                old_data = {**data}
                old_data['unk'] = list(np.copy(data['unk']))
                old_data['true'] = list(np.copy(data['true']))
                old_data['false'] = list(np.copy(data['false']))

                literal, data = DP_pick_literal(data['unk'], data)

                # set split into dictionary tree
                save = [problem, old_data, prev_literal]
                tree[literal] = save

                # save this literal as the previous for the next split
                prev_literal = literal

                nr_splits += 1

            # if this path returns an unsatisfiable configuration,
            # traverse back through the tree and try different splits
            else:

                # so this is the previous problem!
                #print(tree[prev_literal][0])

                problem, data, tree, literal = backtrack(tree, data, literal, unknown_starts, [])

                prev_literal = literal
                #if chosen_lit is not None:
                #    literal = chosen_lit

            print(tree.keys())

        else:
            return data["true"]

        # check if dead end!


        ############################
        # step 4, rinse and repeat #
        ############################

"""
START WITH A SIMPLE BACKTRACK OF ONE VARIABLE
"""
def backtrack(tree, data, literal, unknown_starts, seen_literals):

    # step 1, get all the old values back
    old_problem = tree[literal][0]

    old_data = tree[literal][1]


    data_to_save = {**old_data}
    data_to_save['unk'] = list(np.copy(data_to_save['unk']))
    data_to_save['true'] = list(np.copy(data_to_save['true']))
    data_to_save['false'] = list(np.copy(data_to_save['false']))


    prev_literal = tree[literal][2]


    # PREV LITERAL WILL LEAD YOU TO THE PREVIOUS PROBLEM

    # step 2, check whether the counterpart of the variable has been used yet

    # if both have been seen and they are the first choice, we choose a new starting point from the unknown start points
    if -literal in tree.keys() and prev_literal == 0:

        # pick a new starting unknown
        literal, data = DP_pick_literal(unknown_starts, old_data)

        # remove the literal from the unknown starts, since it will no longer be unknown
        unknown_starts.remove(abs(literal))

        # now reinitialize tree (since the previous literal was 0 anyway) old entries
        tree = {}
        tree[literal] = [old_problem, data_to_save, prev_literal]

        #return old_problem, data, tree, literal


    # if it has, backtrack, let's say it has not yet
    elif -literal in tree.keys():

        # use the prev literal found in the node until this is no longer true
        seen_literals.append(literal)
        seen_literals.append(-literal)
        seen_literals = list(set(seen_literals))

        seen_literals = backtrack(tree, data, prev_literal, unknown_starts, seen_literals)
        return seen_literals

        # so we use recursion until we end up in the old loop
        #print("QUITTING")
        #quit()

    # start with what happens if the variable has not yet been seen
    else:
        # flip the variable of the literal, by moving it from true to false or vice versa, depending on value
        # use the CURRENT data for this, but not the current problem

        # if it is a negative, remove it from false and insert it to true
        if literal < 0:
            data['false'].remove(abs(literal))
            data['true'].append(abs(literal))

            # sanity check
            #if abs(literal) in data['false']:
            #    print("FOUND LITERAL " + str(literal) + " IN THE FALSE LIST")

        else:
            data['true'].remove(abs(literal))
            data['false'].append(abs(literal))

            # sanity check
            # if abs(literal) in data['true']:
            #    print("FOUND LITERAL " + str(literal) + " IN THE TRUE LIST")

        #print("TREE:")
        #print(tree.keys())
        #print("INSERTING " + str(literal) + " INTO THE TREE")
        # since the literal has been flipped, we insert its counterpart
        # into the tree with the old problem and the new data

        # misschien hier niet old data, dan zit je namelijk meteen weer vast
        # TODO CHECK WAT VOOR DATA HIER UITKOMT VERGELEKEN MET DE COUNTERPICK

        tree[-literal] = [old_problem, old_data, prev_literal]

        for lit in seen_literals:
            del tree[lit]

        print("BACK TO SPLITTING")

        #print()



    # step 3, use this and recheck the problem, for this we return the OLD_PROBLEM and the MANIPULATED CURRENT data

    return old_problem, data, tree, literal

def DP_pick_literal(choose_from, data):

    # choose variable to be flipped
    literal = random.choice(choose_from)

    # remove this variable from the unknown variables
    data['unk'].remove(literal)

    # randomly set variable to true or false
    x = random.random()
    if x >= 0.5:
        data['true'].append(literal)

    else:
        data['false'].append(literal)

        # set to minus value to indicate that a value of false was chosen (for purpose of the tree dict)
        literal = -literal

    return literal, data


solution = SATsolver("output.txt", "sudoku-rules.txt")

sudoku = np.zeros((9,9))

for code in solution:
    code = str(code)

    sudoku[int(code[0]) - 1, int(code[1]) - 1] = int(code[2])

print(sudoku)
