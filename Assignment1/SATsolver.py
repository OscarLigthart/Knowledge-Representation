import itertools as it
import numpy as np
import random

class Node:
    """
    Class Node
    """
    def __init__(self, bool_data, problem, literal):
        self.left = None
        self.literal = literal
        self.data = bool_data
        self.problem = problem
        self.right = None

class Tree:
    """
    Class tree will provide a tree as well as utility functions.
    """

    def createNode(self, bool_data, problem, literal):
        """
        Utility function to create a node.
        """
        return Node(literal, bool_data, problem)

    def insert(self, node, bool_data, problem, bool, literal):
        """
        Insert function will insert a node into tree.
        Duplicate keys are not allowed.
        """
        # if tree is empty , return a root node
        if node is None:
            return self.createNode(bool_data, problem, literal)
        # if data is smaller than parent , insert it into left side
        # TODO: measure when left and when right
        if bool == 1:
            node.left = self.insert(node.left, bool_data, problem, bool, literal)
        elif bool == 0:
            node.right = self.insert(node.right, bool_data, problem, bool, literal)

        return node

    def search(self, node, data):
        """
        Search function will search a node into tree.
        """
        # if root is None or root is the search data.
        if node is None or node.data == data:
            return node

        if node.data < data:
            return self.search(node.right, data)
        else:
            return self.search(node.left, data)

    def traverseInorder(self, root):
        """
        traverse function will print all the node in the tree.
        """
        if root is not None:
            self.traverseInorder(root.left)
            print(root.left)
            print(root.right)
            self.traverseInorder(root.right)

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


def SATsolver(sud_input, rules_input):
    '''
    This function takes as input the DIMACS format of a sudoku and the DIMACS format of the sudoku rules to correctly
    Solve a sudoku
    '''

    # TODO read the rules
    problem = []
    nr_variables = ""
    nr_rules = ""
    with open(rules_input, 'r') as f:
        lines = f.read().splitlines()

        firstline = True

        # for each word in the line:
        for line in lines:

            if firstline:
                info = line.split()
                nr_variables = info[2]
                nr_rules = info[3]
                firstline = False
                continue

            rule = line.split()

            del rule[-1]

            rule = [int(i) for i in rule]

            problem.append(rule)



    # TODO GENERALIZE

    variables = list(set(abs(var) for clause in problem for var in clause))
    data = {'true': [], 'false': [], 'unk': []}

    # set all variables to unknown
    for var in variables:
        data['unk'].append(var)

    # TODO GENERALIZE

    with open(sud_input, 'r') as f:
        lines = f.read().splitlines()

        for line in lines:

            rule = line.split()
            del rule[-1]

            for var in rule:
                data['true'].append(int(var))

    # TODO solve

    # keep track of count to prevent infinite loop
    count = 0

    # initialize dictionary
    pure_literal_dict = {}

    # create tree to keep track of splits made
    root = None
    path = Tree()
    root = path.insert(root, data, problem, 0, 0)

    #node, bool_data, dictionary

    # loop while the problem is still not solved
    while len(problem) > 0 and count < 100:
        count += 1

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

                    # remove the clause if literal within is true
                    else:
                        remove = True

                elif abs(literal) in data['false']:
                    # check if it is a positive, remove the literal if it is a positive
                    if literal > 0:
                        new_clause.remove(literal)

                    # remove the clause if literal within is false
                    else:
                        remove = True

            if not remove:
                new_problem.append(new_clause)

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

                # keep track of positive and negative occurences of literals to find pure literals
                if literal > 0:
                    pure_literal_dict[abs(literal)]["pos"] += 1

                elif literal < 0:
                    pure_literal_dict[abs(literal)]["neg"] += 1

            if not taut:
                new_problem.append(clause)

        problem = new_problem

        # SANiTY CHECK FOR PURE LITERALS
        """
        for i, clause in enumerate(problem):
            for j, literal in enumerate(clause):
                if literal == 114:
                    print(clause)
                    print(i)
                    print(count)
        """


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

            # if there are no negatives, set the literal to true
            elif neg == 0 and pos != neg:
                data['true'].append(literal)
                try:
                    data['unk'].remove(literal)
                except:
                    pass

        data['false'] = list(set(data['false']))
        data['true'] = list(set(data['true']))

        # sanity check
        # TODO, check if lists hold unique elements accross, element can't be true and false

        ##############################
        # step 3, split if necessary #
        ##############################

        # check if necessary
        if len(problem) > 0:

            # apply split
            # pick random value from unknowns and set it to either true or false
            if len(data['unk']) > 0:
                literal = random.choice(data['unk'])

                data['unk'].remove(literal)

                if random.random() >= 0.5:
                    data['true'].append(literal)
                    val = 1
                else:
                    data['false'].append(literal)
                    val = 0

                # save current state (as node)
                path.insert(root, data, problem, val, literal)

            # if there are no more unknowns, traverse back through the tree and try different splits
            else:
                # need a backtracking function for the tree
                path.traverseInorder(root)

        else:
            break

        # check if dead end!
        # might go wrong because of this? why?

        ############################
        # step 4, rinse and repeat #
        ############################

    print(len(data['true']))

    return


solution = SATsolver("output.txt", "sudoku-rules.txt")

print(solution)
