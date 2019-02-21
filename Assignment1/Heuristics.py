import numpy as np
import random

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




