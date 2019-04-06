import itertools
from collections import defaultdict
from graphviz import Digraph

class QRModel:
    def __init__(self, quantities, derivatives, proportionality, influence, value_correspondences, leave_trace):
        self.quantities = quantities
        self.derivatives = derivatives
        self.vc = value_correspondences
        self.proportionality = proportionality
        self.influence = influence
        self.leave_trace = leave_trace
        self.trace = {}
        if leave_trace:
            self.gen_valid_states()

    def gen_states(self):

        """Generate all possible states"""

        #all_permutations = [self.quantities['I'], self.quantities['V'], self.quantities['O'],
        #                    self.derivatives, self.derivatives, self.derivatives]

        all_permutations = []

        for key, value in self.quantities.items():
            all_permutations.append(value)

        for i in range(len(self.quantities)):
            all_permutations.append(self.derivatives)

        pre_states = list(itertools.product(*all_permutations))

        states = []
        # order the states --> two lists where one is magnitude and the other is derivative
        for state in pre_states:
            new_state = {}
            for i, key in enumerate(self.quantities.keys()):
                new_state[key] = {}
                new_state[key]['magnitude'] = state[i]
                new_state[key]['derivative'] = state[len(self.quantities) + i]
            states.append(new_state)

        self.all_states = states
        return states

    def gen_valid_states(self):

        # generate all states
        self.gen_states()

        # filter states
        self.vc_filter()

        trace_states = self.valid_state(self.filtered_states)

        # create dictionary for all possible state combinations to keep track of trace
        if self.leave_trace:
            for state1 in trace_states:
                for state2 in trace_states:
                    if state1 != state2:
                        self.trace[str(state1) + str(state2)] = {}


    def vc_filter(self):
        """
        This function removes the states that are impossible to occur on the account of value correspondences
        :return:
        """

        filtered_states = []

        # loop over all states
        for state in self.all_states:

            # set boolean to check if state is valid
            valid = True

            # check for all value correspondencies
            for value_correspondence in self.vc:

                # todo: make syntax for value correspondences
                # decode vc --> [quantity1, value1, quantity2, value2]
                quantity1 = value_correspondence[0]
                value1 = value_correspondence[1]
                quantity2 = value_correspondence[2]
                value2 = value_correspondence[3]

                # if we find for quantity 1, value1, then quantity2 has to be value2
                if state[quantity1]['magnitude'] == value1:
                    if state[quantity2]['magnitude'] != value2:
                        # set state to false validity
                        valid = False

            if valid:
                filtered_states.append(state)


        filtered_states = self.landmark_filter(filtered_states)

        self.filtered_states = filtered_states

        return filtered_states

    def landmark_filter(self, states):
        """
        This function excludes states that have positive derivatives on a max state and negative derivatives
        on a 0 state
        """

        filtered_states = []
        for state in states:

            valid = True

            # for each quantity, if it is max derivative can not be plus, or if it is 0 derivative can not be negative
            for q in self.quantities.keys():
                if (state[q]['magnitude'] == 'max' and state[q]['derivative'] == '+') or \
                        (state[q]['magnitude'] == '0' and state[q]['derivative'] == '-'):
                    valid = False

            if valid:
                filtered_states.append(state)

        return filtered_states


    def transition_states(self, curr_state, exogenous =True):
        """
        Determine all possible changes that can occur from the current state
        :return:
        """

        # for a transition to be possible we need: same values, changed values based on derivative
        # check all derivatives and find next quantity for these derivatives
        # all derivatives need to be satisfied at once for a state to be candidate for a valid transition

        ###################################################################
        # First get changes in magnitude on the account of the derivative #
        ###################################################################

        subs = defaultdict(list)
        for quantity, values in curr_state.items():

            subs[quantity].append(values)

            mag = values['magnitude']
            der = values['derivative']

            # check if the current derivative is 0 and change it
            if der == '0':
                # change it in both directions, except for inflow?
                if quantity == "I":
                    pass
                else:
                    subs[quantity].append({'magnitude': mag, 'derivative': '+'})

                    subs[quantity].append({'magnitude': mag, 'derivative': '-'})


            # if there already exists a derivative, change the magnitude in its direction
            # if magnitude reaches landmark, set derivative to 0
            else:
                # get the index of the current magnitude
                ind = self.quantities[quantity].index(mag)

                # change it according to positive derivative
                if der == '+':
                    if quantity == 'I':
                        new_mag = self.quantities[quantity][min(1, ind + 1)]
                    else:
                        new_mag = self.quantities[quantity][ind + 1]
                elif der == '-':
                    new_mag = self.quantities[quantity][ind - 1]

                # create all possible changes in magnitude with all new derivatives
                # inflow can be changed at any state since it is exogenous, but remains the same when other
                # values change
                if quantity == 'I' and new_mag != mag:
                    if der == '-':
                        subs[quantity].append({'magnitude': new_mag, 'derivative': '0'})
                    else:
                        subs[quantity].append({'magnitude': new_mag, 'derivative': der})
                elif quantity == 'I' and new_mag != '0':
                    pass
                else:
                    for derivative in self.derivatives:
                        subs[quantity].append({'magnitude': new_mag, 'derivative': derivative})

                    # also add the old value with changed magnitude for ambiguity?
                    # change the derivative in which direction? (change it by one)
                    # -->
                    if der == "-":
                        subs[quantity].append({'magnitude': mag, 'derivative': "-"})
                        subs[quantity].append({'magnitude': mag, 'derivative': "0"})
                    elif der == "+":
                        subs[quantity].append({'magnitude': mag, 'derivative': "+"})
                        subs[quantity].append({'magnitude': mag, 'derivative': "0"})
                    else:
                        for derivative in self.derivatives:
                            subs[quantity].append({'magnitude': mag, 'derivative': derivative})

        # print()
        # print('CURRENT STATE:')
        # print()
        # print(curr_state)
        # print()

        transition_states = []

        for perm in itertools.product(*subs.values()):

            # Create a new state object
            new_state = {}
            for i, quantity in enumerate(self.quantities):
                new_state[quantity] = perm[i]

            # check if the generated state is among the filtered (possible) states
            if new_state in self.filtered_states and new_state != curr_state:
                transition_states.append(new_state)

                ############################################
                # Leave a trace for changing the magnitude #
                ############################################
                if self.leave_trace:
                    if self.valid_state([new_state]):
                        # trace:
                        # extract the magnitudes to find why it changes
                        # self.trace[str(new_state)] = {}
                        # self.trace[str(new_state)][
                        #     'inter'] =

                        # find the changes in states and blame the derivative for their changes
                        # magnitude becomes: , due to derivative of:


                        sample_text = '\nThis state is a result of the following changes:\n'
                        text = ''

                        val = False
                        for quan in self.quantities:
                            if new_state[quan]['magnitude'] != curr_state[quan]['magnitude']:
                                text += '{} gets a magnitude of {}, due to the previous magnitude of {} having'\
                                        ' a derivative of {}\n'\
                                    .format(quan, new_state[quan]['magnitude'],
                                            curr_state[quan]['magnitude'], curr_state[quan]['derivative'])
                                val = True

                        if val:
                            self.trace[str(curr_state) + str(new_state)]['inter'] = sample_text + text

                        else:
                            if curr_state['I']['derivative'] == '+':
                                # here the trace that inflow is getting stronger
                                self.trace[str(curr_state) + str(new_state)]['inter'] = \
                                    'The inflow is getting stronger compared to the outflow '\
                                        'so the derivative of V changes from {} to {}'\
                                        .format(curr_state['V']['derivative'], new_state['V']['derivative'])
                            else:
                                # here the trace that inflow is getting weaker
                                self.trace[str(curr_state) + str(new_state)]['inter'] = \
                                    'The inflow is getting weaker compared to the outflow ' \
                                    'so the derivative of V changes from {} to {}' \
                                        .format(curr_state['V']['derivative'], new_state['V']['derivative'])

        ###############################
        # exogenous state transitions #
        ###############################

        subs = defaultdict(list)
        for quantity, values in curr_state.items():
            mag = values['magnitude']
            der = values['derivative']
            # inflow is exogenous, so can be changed at will, however: follow magnitude changes
            if quantity == "I":

                # change magnitude
                # get the index of the current magnitude
                ind = self.quantities[quantity].index(mag)

                # change the derivative of quantity
                if der == '+':
                    new_mag = self.quantities[quantity][min(1, ind + 1)]
                    subs[quantity].append({'magnitude': new_mag, 'derivative': '0'})
                elif der == '-':
                    new_mag = self.quantities[quantity][ind - 1]
                    subs[quantity].append({'magnitude': new_mag, 'derivative': '0'})
                else:
                    subs[quantity].append({'magnitude': mag, 'derivative': '-'})
                    subs[quantity].append({'magnitude': mag, 'derivative': '+'})

            # keep original values for other quantities, except when on landmark
            # instead: follow derivative changes
            else:
                subs[quantity].append(values)


        # add the exogenous transitions to the set of possible transitions
        if exogenous:

            for perm in itertools.product(*subs.values()):

                # Create a new state object
                new_state = {}
                for i, quantity in enumerate(self.quantities):
                    new_state[quantity] = perm[i]

                # check if the generated state is among the filtered (possible) states
                if new_state in self.filtered_states and new_state != curr_state and new_state not in transition_states:

                    # check if valid over here
                    transition_states.append(new_state)

                    #######################################
                    # Leave a trace for exogenous actions #
                    #######################################
                    if self.leave_trace:
                        if self.valid_state([new_state]):
                            # trace:
                            self.trace[str(curr_state)+str(new_state)]['inter'] = \
                                'This state is a result of an exogenous action, '\
                                    'where a person manually operates the inflow.'

        # now we have all the possible transitions from a single state!
        transition_states = self.valid_state(transition_states, curr_state)

        return transition_states

    def valid_state(self, states, curr_state = None):
        """
        This function checks whether a given state is valid according to influence, proportionality and...
        :param state: state to consider
        :return:
        """
        # check influence and proportion ratio
        # see if that is valid --> volume derivative can not be + if there is no inflow
        valid_states = []

        for i, state in enumerate(states):
            # a state needs to be valid according to proportionality and influence
            # keep track of the influences on the derivatives for every quantity

            #############################
            # Proportionality/Influence #
            #############################

            check = self.find_proportionality(state)

            derivs = self.find_influence(state)

            # check if all proportionalities are satisfied, then use the calculus rules to determine whether ambiguity
            # occurs
            if all(check):

                # check for all zeros
                if all([x == 0 for x in derivs['V']]):
                    # check whether derivative actually is 0
                    if state['V']['derivative'] == '0':
                        valid_states.append(state)

                        # trace
                        if curr_state != None and self.leave_trace:

                            # print('Derivative should be 0 as there is no effect')
                            self.trace[str(curr_state) + str(state)]['intra'] = \
                                'Derivative of V should be 0, as there is no influence'


                        # sum and check if positive or negative
                elif sum(derivs['V']) > 0:

                    # check whether the derivative actually is positive
                    if state['V']['derivative'] == '+':
                        valid_states.append(state)

                        # trace
                        if curr_state != None and self.leave_trace:
                            # print('Derivative should be 0 as there is no effect')
                            self.trace[str(curr_state) + str(state)]['intra'] = \
                                'Derivative of V should be +, as there is only positive influence'

                elif sum(derivs['V']) < 0:
                    # check whether the derivative actually is negative
                    if state['V']['derivative'] == '-':
                        valid_states.append(state)

                        # trace
                        if curr_state != None and self.leave_trace:
                            # print('Derivative should be 0 as there is no effect')
                            self.trace[str(curr_state) + str(state)]['intra'] = \
                                'Derivative of V should be -, as there is only negative influence'

                # sum and check if 0
                elif sum(derivs['V']) == 0:
                    # return state with all derivatives
                    valid_states.append(state)

                    # trace
                    if curr_state != None and self.leave_trace:

                        #trace
                        if state['V']['derivative'] == '-':
                            self.trace[str(curr_state) + str(state)]['intra'] = \
                                'In this case the outflow is stronger than the inflow, so the derivative of V is -'\
                                ' (ambiguous)'

                        elif state['V']['derivative'] == '+':
                            self.trace[str(curr_state) + str(state)]['intra'] = \
                                'In this case the inflow is stronger than the outflow, so the derivative of V is +'\
                                ' (ambigous)'

                        else:
                            self.trace[str(curr_state) + str(state)]['intra'] = \
                                'In this case the inflow is as strong as the outflow, so the derivative of V is 0' \
                                ' (ambiguous)'

        return valid_states

    def find_proportionality(self, state):
        """
        This function checks whether a state is valid according to the proportional relation between quantities
        :param state:
        :return:
        """

        # find where proportionalities occur
        props = self.proportionality

        check = []
        # for every proportional relation, check if the state follows the rule
        for prop in props:
            quantity1 = prop[0]
            relation = prop[1]
            quantity2 = prop[2]

            # when something is proportional, the derivatives need to be the same
            if relation == 'P-':
                # the derivatives have to be opposite to each other in this case
                # find the index of the derivative and
                ind = self.derivatives.index(state[quantity1]['derivative'])

                # take the opposite derivative --> if ind == 2 it has to be 0 and vice versa
                opp_der = self.derivatives[abs(ind-2)]

                if state[quantity2]['derivative'] == opp_der:
                    check.append(True)
                else:
                    check.append(False)

            elif relation == 'P+':
                if state[quantity1]['derivative'] == state[quantity2]['derivative'] and \
                        state[quantity1]['magnitude'] == state[quantity2]['magnitude']:
                    check.append(True)
                else:
                    check.append(False)


        return check

    def find_influence(self, state):
        """
        This function checks whethr a state is valid according to the influence relation between quantities
        :param state:
        :return:
        """

        influences = self.influence

        #valid = False

        derivs = defaultdict(list)

        for inf in influences:
            quantity1 = inf[0]
            relation = inf[1]
            quantity2 = inf[2]

            # check for positive influence
            if relation == 'I+':
                # check if there is some magnitude of the quantity in a state
                # if there is, the derivative of the other quantity should be positive
                #if state[quantity1]['magnitude'] != '0' and state[quantity2]['derivative'] == '+':
                if state[quantity1]['magnitude'] != '0':
                    # return the type of influence
                    #valid = True
                    derivs[quantity2].append(1)

                # if it is 0 there is no influence
                else:
                    derivs[quantity2].append(0)
                    # return the type of influence
                    #valid = False
                    #return False

            # check for negative influence
            elif relation == 'I-':

                # check if there is some magnitude of the quantity in a state
                # if there is, the derivative of the other quantity should be negative
                if state[quantity1]['magnitude'] != '0':
                    #valid = True
                    derivs[quantity2].append(-1)

                else:
                    derivs[quantity2].append(0)
                    #valid = False

                    # return False

        return derivs


def main():


    # Quantity spaces:
    # inflow [0,+]
    # outflow [0,+,max]
    # derivatives [-,0,+]

    # generate the quantities in model
    quantities = {
        'I': ['0', '+'],
        'V': ['0', '+', 'max'],
        'O': ['0', '+', 'max'],
    }

    # generate the possible derivatives
    derivatives = ['-', '0', '+']

    # introduce dependencies
    # I --(I+)--> V
    # O --(I-)--> V
    # V --(P+)--> O

    # insert the proportionalities
    p1 = ["V", "P+", "O"] # V --(P+) -> O
    props = [p1]

    # insert the influences
    i1 = ["I", "I+", "V"]  # I --(I+)-> V
    i2 = ["O", "I-", "V"] # O --(I-)-> V
    influences = [i1, i2]

    # determine value_correspondences --> [quantity1, value1, quantity2, value2]
    vc1 = ["V", "max", "O", "max"]
    vc2 = ["V", "0", "O", "0"]
    value_correspondence = [vc1, vc2]

    extension = True
    if extension:
        quantities.update({
            "H": ["0", "+", "max"],
            "P": ["0", "+", "max"]
        })

        # Volume   --(P+)--> Height
        # Height   --(P+)--> Pressure
        # Pressure --(P+)--> Outflow
        p1 = ["V", "P+", "H"]
        p2 = ["H", "P+", "P"]
        p3 = ["P", "P+", "O"]

        props = [p1, p2, p3]

        vc1 = ["V", "max", "H", "max"]
        vc2 = ["V", "0", "H", "0"]
        vc3 = ["H", "max", "P", "max"]
        vc4 = ["H", "0", "P", "0"]
        vc5 = ["P", "max", "O", "max"]
        vc6 = ["P", "0", "O", "0"]

        value_correspondence = [vc1, vc2, vc3, vc4, vc5, vc6]

    """
    model = QRModel(quantities, derivatives, props, influences, value_correspondence, True)
    states = model.gen_states()
    filtered_states = model.vc_filter()

    transitions = model.transition_states(filtered_states[0])

    print('---------------------------------')
    print('Possible state to transition to:')
    print('---------------------------------')

    print(transitions)

    #print(transitions)

    trans3 = model.transition_states(transitions[0])

    print('---------------------------------')
    print('Possible state to transition to:')
    print('---------------------------------')

    for tr in trans3:

        print('INTER STATE trace:')
        print(model.trace[str(transitions[0]) + str(tr)]['inter'])

        print()
        print('INTRA STATE trace:')
        print(model.trace[str(transitions[0]) + str(tr)]['intra'])
        print()
        print(tr)
        print()

    bla = trans3[0]
    trans3 = model.transition_states(trans3[0])

    print('---------------------------------')
    print('Possible state to transition to:')
    print('---------------------------------')

    for tr in trans3:
        print('INTER STATE trace:')
        print(model.trace[str(bla) + str(tr)]['inter'])

        print()
        print('INTRA STATE trace:')
        print(model.trace[str(bla) + str(tr)]['intra'])
        print()
        print(tr)
        print()

    bla = trans3[0]
    trans3 = model.transition_states(trans3[0])

    print('---------------------------------')
    print('Possible state to transition to:')
    print('---------------------------------')

    for tr in trans3:
        print()
        print(tr)
        print()
        print('INTER STATE trace:')
        print(model.trace[str(bla) + str(tr)]['inter'])

        print()
        print('INTRA STATE trace:')
        print(model.trace[str(bla) + str(tr)]['intra'])
        print()
        print(tr)
        print()
        
    """

    # create model
    model = QRModel(quantities, derivatives, props, influences, value_correspondence, True)

    # generate and filter all states
    states = model.gen_states()
    filtered_states = model.vc_filter()

    # get all valid states to create nodes
    valid_states = model.valid_state(filtered_states)

    print(len(valid_states))

    nodename = {}

    transitions = defaultdict(list)

    node_ID = {}

    letter = 65 #ascii

    for state in valid_states:

        node_ID[str(state)] = chr(letter)
        letter += 1

        # create node 'name'
        s = "Q | M   D\n--+------\n"
        for quan, values in state.items():
            s += "{} | {:4s}{}\n".format(quan, values['magnitude'], values['derivative'])
        nodename[str(state)] = s

        # get all transitions
        next_states = model.transition_states(state)

        print('------------------------')
        print('NEW STATE')
        print('-------------------------')
        # store all transitions
        for next_state in next_states:
            transitions[str(state)].append(str(next_state))
            print('Curr state:')
            print(state)
            print()
            print('Next state:')
            print(next_state)

        node_ID[str(state)] = chr(letter)
        letter += 1 

    # get all transitions from valid states
    #state graph

    dot = Digraph('unix', filename='stategraph.gv')

    dot.node_attr.update(color='lightblue2', style='filled', shape='box', fontsize='20', fontname='Helvetica', height='0', width='0')
    dot.edge_attr.update(arrowhead='vee', arrowsize='0.5', arrowtail="both")

    edges_graph = []

    for key, name in nodename.items():

        dot.node(node_ID[key], name)
        
        for trans in transitions[key]:
            edges_graph.append(node_ID[key] + node_ID[trans])


    edges_graph = list(set(edges_graph))

    dot.edges(edges_graph)

    dot.view()


main()
