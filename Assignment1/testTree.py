import random
import copy

class Node:
    """
    Node to store dat at split
    """

    def __init__(self, _variable, _var_assignment, _problem,  _data):
        self.variable = _variable
        self.var_assignment = _var_assignment # either true or false

        self.child_true = None
        self.child_false = None

        self.data = _data # partial solution
        self.problem = _problem # remaining problem

        self.parent = None # keep track of parent node

class Tree:
    """
    Class tree will provide a tree as well as utility functions.
    """
    def __init__(self, _problem, _data):

        self.root_node = Node(None, None, _problem, _data) # root_node only contains the problem and data
        self.current_node = self.root_node

    def createNode(self, variable, var_assignment, problem, data):
        """
        Creates a node representing a split with the variable and its assigned value
        """
        return Node(variable, var_assignment, problem, data)


    def insert(self, new_node, parent_node, var_assignment):
        """
        Inserts the new node in the tree
        """

        # depending on the value assigned to the variable, the node will be connected to either the "assigned true" side
        # or the "assigned false" side
        if var_assignment == True:
            self.current_node.child_true = new_node

        if var_assignment == False:
            self.current_node.child_false = new_node

        # keep track of the parent
        new_node.parent = parent_node

    def split(self):
        """
        pick randomly a variable which is still present in the problem and assign it to be either true of false
        create a new node for this split and insert it in the tree
        """

        print("SPLIT")

        # this is the current problem we need to solve
        current_problem = self.current_node.problem

        print("current PROBLEM", current_problem)

        # pick randomly a variable that still occurs in the current problem
        variable = abs(random.choice(random.choice(current_problem)))

        print("current var", variable)

        # and randomly assign a value (true or false) to this variable
        var_assignment = bool(random.getrandbits(1))

        # remember the value we assigned to this variable by storing it in the data
        updated_data = copy.deepcopy(self.current_node.data)
        if var_assignment == True:
            updated_data["true"].add(variable)
        elif var_assignment == False:
            updated_data["false"].add(variable)

        print("new data", updated_data)

        # now this variable has a value assigned, the problem will change: so update the problem
        updated_problem = update_problem(current_problem, variable, var_assignment)

        print("new problem", updated_problem)
        # since we made a new split (new assignment for a variable), we need to create a new node representing this assignment
        new_node = self.createNode(variable, var_assignment, updated_problem, updated_data)

        # and insert in the right position in the tree
        self.insert(new_node, self.current_node, var_assignment) # the current node will be the parent of the new node

        # make sure we are always at the most recent node in the solution space
        # therefore make this new node the current_node
        self.current_node = new_node

    def backtrack(self):
        """
        go back to previous split
        """

        print("BACKTRACK")

        print("current node", self.current_node)
        print("current node", self.current_node.variable)
        print("current node", self.current_node.var_assignment)

        while(True):
            # get the parent of the current node
            parent = self.current_node.parent

            # and see if there is an opportunity to reassign the variable of the current node
            # (there is an opportunity if one of the assignments isnt tried yet (aka either child_false or child_true needs
            # to be None (it is False when it is already tried)

            # if the variable is currently assigned to true and we didn't try to assign it to false yet
            if self.current_node.var_assignment == True and parent.child_false == None:

                print("1")

                # so assign the variable to false this time
                parent.child_false = self.current_node
                self.current_node.var_assignment = False

                parent.child_true = False # set from None to False; indicating that we already tried that option

                # use the data of the parent to create the new data, with the variable now assigned to false
                updated_data = copy.deepcopy(parent.data)
                updated_data["false"].add(self.current_node.variable)

                # use the problem of the parent to create the new problem with the variable now assigned to false
                updated_problem = update_problem(parent.problem, self.current_node.variable, self.current_node.var_assignment)

                # and update the node with the new data and problem
                self.current_node.data = updated_data
                self.current_node.problem = updated_problem

                print("current node1", self.current_node)
                print("current node1", self.current_node.variable)
                print("current node1", self.current_node.var_assignment)


            # if the variable is currently assigned to false and we didn't try to assign it to true yet
            elif self.current_node.var_assignment == False and parent.child_true == None:

                print("2")

                # so assign the variable to true this time
                parent.child_true = self.current_node
                self.current_node.var_assignment = True
                parent.child_false = False # set from None to False; indicating that we already tried that option

                # use the data of the parent to create the new data, with the variable now assigned to true
                updated_data = copy.deepcopy(parent.data)
                updated_data["true"].add(self.current_node.variable)

                # use the problem of the parent to create the new problem , with the variable now assigned to true
                updated_problem = update_problem(parent.problem, self.current_node.variable, self.current_node.var_assignment)

                # and update the node with the new data and problem
                self.current_node.data = updated_data
                self.current_node.problem = updated_problem

                print("current node2", self.current_node)
                print("current node2", self.current_node.variable)
                print("current node2", self.current_node.var_assignment)

            elif self.current_node == self.root_node:
                # the problem is unsatisfiable: we backpropagated all the way back to the root note, and even in this
                # in this root note we already tried to assign its child to be true or false (aka we searched the whole solution space)
                return False

            empty_clause = False
            for clause in tree.current_node.problem:
                if clause == []:
                    empty_clause = True
            # no options left in this node, so we need to go further up in the tree

            # if there is still a empty clause, this could be due to two reasons:
            # 1) we already tried to assign the variable to true and false (we didnt get in the if statements so nothing changed)
            #   --> solution: need to go higher up in the tree cause we already tried everything here
            # 2 reassigning the variable doesn't solve the empty claus problem
            #   --> solution: this means the problem is higher up in the tree. so we need to go higher up in tree
            if empty_clause:
                print("go back to parent")
                self.current_node = parent
                print("parent prob", self.current_node.problem)
                print("parent data", self.current_node.data)
            else:
                return True # backtracking was successful (aka resulted in a problem without empty clauses)


def update_problem(problem, variable, var_assignment):
    """
        updates the problem after variable is set to a certain value
    """
    new_problem = []

    for clause in problem:
        new_clause = copy.deepcopy(clause)
        clause_satisfied = False

        for literal in clause:

            # if the variable appears in the clause
            if abs(literal) == variable:

                # if the variable appears as a neg. literal
                if literal < 0:

                    # and the variable is assigned to true, the outcome will be "not" true -> so false
                    if var_assignment == True:
                        # in that case the literal needs to be removed from the clause
                        new_clause.remove(literal)

                    # however, if the variable is assigned to false, the outcome will be "not" false -> so true
                    elif var_assignment == False:
                        # in that case the clause is satisfied
                        clause_satisfied = True
                # if the variable appears as a pos. literal
                else:

                    # and the variable is assigned to true, the outcome will be true
                    if var_assignment == True:
                        # in that case the clause is satisfied
                        clause_satisfied = True

                    # however, if the variable is assigned to false, the outcome will be false
                    if var_assignment == False:
                        # in that case the literal needs to be removed from the clause
                        new_clause.remove(literal)

        # if the clause is not satisfied, it will remain in the problem
        if not clause_satisfied:
            new_problem.append(new_clause)

    return new_problem



problem = [[1, -2],[1, -3, 2],[3, 2, -1],[-2 ,-1, 3]]
data = {'true': set(), 'false': set()}


# initialize the tree
tree = Tree(problem, data)


# continue reducing the problem until we find either a solution to this problem (aka empty problem list) or we find that there
# is no solution to this problem (aka problem is not satisfiable)

satisfiable = True
while(tree.current_node.problem != [] and satisfiable):

        empty_clause = False
        while(True):
            # SIMPLIFY
            # code to simplify goes in here

            # and update the current in the tree with this simplification
            # tree.current_node.problem = problem_after_simplification
            # tree.current_node.data = data_after_simplification

            tree.split()

            if tree.current_node.problem == []:
                break

            for clause in tree.current_node.problem:
                if clause == []:
                    empty_clause = True

            if empty_clause:
                break

        if empty_clause:

            statisfiable = tree.backtrack()


print("SAT", satisfiable)
print(tree.current_node.problem) # return
print(tree.current_node.data)# if a variable is still unassigned, this variable could be either true or false. both count as solution


