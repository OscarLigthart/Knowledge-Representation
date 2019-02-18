import numpy as np

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


    if two_sided_J.get(literal, 0) >= two_sided_J.get(-literal, 0):
        var_assignment = True
    else:
        var_assignment = False

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

        MOM[literal] = ((pos_counts + neg_counts) * 2^k) + (pos_counts * neg_counts)


    # get highest value
    literal = max(MOM, key=MOM.get)

    # two sided MOM?
    if MOM.get(literal, 0) > MOM.get(-literal, 0):
        var_assignment = True
    else:
        var_assignment = False

    return literal, var_assignment




