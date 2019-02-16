import random
import copy
from SATsolver2 import *


class Node:
    """
    Node to store data at each split
    """

    def __init__(self, _variable, _var_assignment, _problem,  _data):
        self.variable = _variable
        self.var_assignment = _var_assignment # either true or false

        self.child_true = None
        self.child_false = None

        self.data = _data # partial solution
        self.problem = _problem # remaining problem

        self.parent = None # keep track of parent node

        self.number = 0 # DEBUG

class Tree:
    """
    SAT solver tree
    """
    def __init__(self, _problem, _data):

        self.root_node = Node(None, None, _problem, _data) # root_node only contains the problem and data
        self.current_node = self.root_node


        self.COUNTER = 0

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

        new_node.number = self.COUNTER
        self.COUNTER +=1

    def split_tree(self):
        """
        pick randomly a variable which is still present in the problem and assign it to be either true of false
        create a new node for this split and insert it in the tree
        """

        print("SPLIT") # DEBUG

        new_problem, new_data, variable, var_assignment = split(self.current_node.problem, self.current_node.data)

        print(variable, var_assignment)

        # since we made a new split (new assignment for a variable), we need to create a new node representing this assignment
        new_node = self.createNode(variable, var_assignment, new_problem, new_data)

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


        while(True):
            # get the parent of the current node

            if self.current_node == self.root_node:
                # the problem is unsatisfiable: we backpropagated all the way back to the root note, and even in this
                # in this root note we already tried to assign its child to be true or false (aka we searched the whole solution space)
                return False

            parent = self.current_node.parent

            # print("current node", self.current_node)
            # print("current node", self.current_node.variable)
            # print("current node", self.current_node.var_assignment)
            # print("node number", self.current_node.number)

            # and see if there is an opportunity to reassign the variable of the current node
            # (there is an opportunity if one of the assignments isnt tried yet (aka either child_false or child_true needs
            # to be None (it is False when it is already tried)

            # if the variable is currently assigned to true and we didn't try to assign it to false yet
            if self.current_node.var_assignment == True and parent.child_false == None:

                print("1")

                # then assign the variable to false this time
                parent.child_false = self.current_node
                self.current_node.var_assignment = False

                parent.child_true = False # set from None to False; indicating that we already tried that option

                # use the data of the parent to create the new data, with the variable now assigned to false
                new_data = update_data(parent.data, self.current_node.variable, self.current_node.var_assignment)

                # use the problem of the parent to create the new problem with the variable now assigned to false
                new_problem = update_problem(parent.problem, self.current_node.variable, self.current_node.var_assignment)

                # and update the node with the new data and problem
                self.current_node.data = new_data
                self.current_node.problem = new_problem

                # print("current node1", self.current_node)
                # print("current node1", self.current_node.variable)
                # print("current node1", self.current_node.var_assignment)


            # if the variable is currently assigned to false and we didn't try to assign it to true yet
            elif self.current_node.var_assignment == False and parent.child_true == None:

                print("2")

                # then assign the variable to true this time
                parent.child_true = self.current_node
                self.current_node.var_assignment = True
                parent.child_false = False # set from None to False; indicating that we already tried that option

                # use the data of the parent to create the new data, with the variable now assigned to true
                new_data = update_data(parent.data, self.current_node.variable, self.current_node.var_assignment)

                # use the problem of the parent to create the new problem , with the variable now assigned to true
                new_problem = update_problem(parent.problem, self.current_node.variable, self.current_node.var_assignment)

                # and update the node with the new data and problem
                self.current_node.data = new_data
                self.current_node.problem = new_problem

                # print("current node2", self.current_node)
                # print("current node2", self.current_node.variable)
                # print("current node2", self.current_node.var_assignment)


            # if there is still a empty clause, this could be due to two reasons:
            # 1) we already tried to assign the variable to true and false (we didnt get in the if statements so nothing changed)
            #   --> solution: need to go higher up in the tree cause we already tried everything here
            # 2 reassigning the variable doesn't solve the empty clause problem
            #   --> solution: this means the problem is higher up in the tree. so we need to go higher up in tree
            if contains_empty_clause(self.current_node.problem):
                print("go back to parent")
                self.current_node = parent
            else:
                return True # backtracking was successful (aka resulted in a problem without empty clauses)