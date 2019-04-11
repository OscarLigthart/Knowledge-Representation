import itertools
from collections import defaultdict
from graphviz import Digraph
import copy
import argparse


class QRModel:
    def __init__(self, quantities, derivatives, proportionality, influence, value_correspondences):
        self.quantities = quantities
        self.derivatives = derivatives
        self.vc = value_correspondences
        self.proportionality = proportionality
        self.influence = influence
        self.landmarks = ['0', 'max']

    def gen_states(self):

        """Generate all possible states"""

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

        # get valid states
        trace_states, _ = self.valid_state(self.filtered_states)



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

        self.valid_states, _ = self.valid_state(filtered_states)

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

    def to_landmark(self, curr_state, next_state):

        """This function checks if a transition occurs from an interval to a landmark"""

        for quantity, values in curr_state.items():
            mag = values['magnitude']
            der = values['derivative']

            if der != '0' and next_state[quantity]['derivative'] == '0':
                return True

            if mag not in self.landmarks and mag != next_state[quantity]['magnitude']:
                return True

        return False


    def from_landmark(self, curr_state, next_state, exogenous):

        """This function check if a transition occurs from a landmark to an interval"""

        for quantity, values in curr_state.items():
            mag = values['magnitude']
            der = values['derivative']

            if mag in self.landmarks and mag != next_state[quantity]['magnitude']:
                return True

            if not exogenous and quantity == "I":
                continue

            if der == '0' and next_state[quantity]['derivative'] != '0':
                return True

        return False

    def transition_states(self, curr_state):
        """
        Determine all possible changes that can occur from the current state
        :return:
        """

        # start with the derivatives --> create a state where all the magnitudes have changed based on the derivatives
        # only change the derivative if we are at a landmark

        subs = defaultdict(list)
        for quantity, values in curr_state.items():

            # should add the same, except when?
            subs[quantity].append(values)

            mag = values['magnitude']
            der = values['derivative']

            # check if the current derivative is 0 and change it
            if der == '0':
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

                # check if new mag falls on landmark, if so derivative becomes 0, else stays on same
                if new_mag in self.landmarks:
                    # get which one it is
                    subs[quantity].append({'magnitude': new_mag, 'derivative': '0'})
                    subs[quantity].append({'magnitude': new_mag, 'derivative': '-'})

                else:
                    subs[quantity].append({'magnitude': new_mag, 'derivative': der})

                # change derivative back to 0
                subs[quantity].append({'magnitude': mag, 'derivative': '0'})

        transition_states = []

        for perm in itertools.product(*subs.values()):

            # Create a new state object
            new_state = {}
            for i, quantity in enumerate(self.quantities):
                new_state[quantity] = perm[i]

            # check if the generated state is among the filtered (possible) states
            if new_state in self.valid_states and new_state != curr_state:
                transition_states.append(new_state)

        valid_trans = copy.deepcopy(transition_states)
        # check if transition is valid
        for state in transition_states:

            # determine whether points comes from or goes to landmark
            from_land = self.from_landmark(curr_state, state, True)
            to_land = self.to_landmark(curr_state, state)

            for quan, values in state.items():
                mag = values['magnitude']
                der = values['derivative']

                # check whether the magnitude changed
                mag_change = False
                if mag != curr_state[quan]['magnitude']:
                    mag_change = True

                # check whether the derivative changed
                der_change = False
                if der != curr_state[quan]['derivative']:
                    der_change = True

                # if they are both changed, the magnitude has to end up in a landmark
                if mag_change and der_change:
                    if mag in self.landmarks:

                        # if the new point is indeed a landmark, then the derivative is allowed to change
                        if not (mag == '0' or (quan != 'I' and mag == 'max')):
                            valid_trans.remove(state)

                # final check for ambiguous state transitions
                if quan == 'I':
                    # get index of derivative of both states for volume
                    curr_deriv = self.derivatives.index(curr_state['V']['derivative'])

                    next_deriv = self.derivatives.index(state['V']['derivative'])


                    # if derivative of inflow is positive, next derivative of volume can not be more
                    # negative compared to first, except when on max
                    if curr_state[quan]['derivative'] == '+' or curr_state[quan]['derivative'] == '0':
                        if next_deriv < curr_deriv:
                            # when on max, derivative can be lower than previous (since it will no longer increase
                            # on max)
                            if state['V']['magnitude'] == 'max' and state['V']['derivative'] == '0':
                                continue

                            try:
                                valid_trans.remove(state)
                            except:
                                pass

                    if curr_state[quan]['derivative'] == '-' or curr_state[quan]['derivative'] == '0':
                        if next_deriv > curr_deriv:
                            # when on 0, derivative can be higher than previous (since it will no longer decrease on 0)
                            if state['V']['magnitude'] == '0' and state['V']['derivative'] == '0':
                                continue
                            try:
                                valid_trans.remove(state)
                            except:
                                pass


            # finally, check whether a point is not coming from a landmark and going to a landmark, since this
            # is impossible
            if not from_land ^ to_land:
                try:
                    valid_trans.remove(state)
                except:
                    pass

        # take all valid transitions that are left
        transition_states = valid_trans

        # only point to interval changes can occur (except for exogenous changes)
        if any(self.from_landmark(curr_state, state, False)
              for state in transition_states):
           transition_states = [state for state in transition_states
                   if self.from_landmark(curr_state, state, True)]

        return transition_states

    def valid_state(self, states):
        """
        This function checks whether a given state is valid according to influence and proportionality
        :param state: state to consider
        :return:
        """
        # check influence and proportion ratio
        # see if that is valid --> volume derivative can not be + if there is no inflow
        valid_states = []

        all_derivs = {}

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

                # sum and check if positive or negative
                elif sum(derivs['V']) > 0:

                    # check whether the derivative actually is positive
                    if state['V']['derivative'] == '+':
                        valid_states.append(state)


                elif sum(derivs['V']) < 0:
                    # check whether the derivative actually is negative
                    if state['V']['derivative'] == '-':
                        valid_states.append(state)

                # sum and check if 0
                elif sum(derivs['V']) == 0:
                    # return state with all derivatives
                    valid_states.append(state)

            all_derivs[str(state)] = derivs

        return valid_states, all_derivs

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

            # when something is proportional, one derivative affects the derivative of the other quantity
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

            # the derivative has to be the same if the proportional relationship is positive
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

        # initiate influences
        influences = self.influence

        # create variable to keep track of calculus matrices
        derivs = defaultdict(list)

        for inf in influences:
            quantity1 = inf[0]
            relation = inf[1]
            quantity2 = inf[2]

            # check for positive influence
            if relation == 'I+':
                # check if there is some magnitude of the quantity in a state
                # if there is, the derivative of the other quantity should be positive
                if state[quantity1]['magnitude'] != '0':
                    # return the type of influence
                    derivs[quantity2].append(1)

                # if it is 0 there is no influence
                else:
                    # return the type of influence
                    derivs[quantity2].append(0)

            # check for negative influence
            elif relation == 'I-':

                # check if there is some magnitude of the quantity in a state
                # if there is, the derivative of the other quantity should be negative
                if state[quantity1]['magnitude'] != '0':
                    derivs[quantity2].append(-1)

                else:
                    derivs[quantity2].append(0)

        return derivs

    def gen_trace(self, curr_state, all_derivs, nodename):
        """ This function generates a trace between the current state and the next state that describes the
        reasoning behind the transition and the next state """


        ######################
        # Show current state #
        ######################
        print('-----------------------------------------------------------------------------')
        print('CURRENT STATE')
        print()
        print(nodename[str(curr_state)])
        print()

        #####################
        # Intra state trace #
        #####################

        # show the intra state trace of the current state
        self.intra_trace(curr_state, all_derivs)

        #########################
        # Show state transition #
        #########################

        # get all next states
        trans_states = self.transition_states(curr_state)

        # print inter trace between current state and all of its possible next states
        for i, next_state in enumerate(trans_states):
            print()
            print('TRANSITION {}:'.format(i+1))
            print()
            self.inter_trace(curr_state, next_state)

        print()
        print('-----------------------------------------------------------------------------')
        print()
        return

    def intra_trace(self, state, all_derivs):

        print('INTRA-state trace:')
        print()

        # what to do for the intra-state trace?
        # influences and proportionalities
        # need to have the behavioural calculus
        derivs = all_derivs[str(state)]

        # check for all zeros
        if all([x == 0 for x in derivs['V']]):
            # check whether derivative actually is 0
            if state['V']['derivative'] == '0':
                print(' - No influence on the volume, so the derivative is 0')

        # sum and check if positive or negative
        elif sum(derivs['V']) > 0:
            # check whether the derivative actually is positive
            if state['V']['derivative'] == '+':
                print(' - Only the inflow is currently influencing the volume, so the volume derivative is +')


        elif sum(derivs['V']) < 0:
            # check whether the derivative actually is negative
            if state['V']['derivative'] == '-':
                print(' - Only the outflow is currently influencing the volume, so the volume derivative is -')


        # sum and check if 0
        elif sum(derivs['V']) == 0:
            # return state with all derivatives
            # ambiguity
            if state['V']['derivative'] == '+':
                print(' - The inflow and outflow are both influencing the volume, but in this case the inflow is stronger than the outflow.\n'
                      '   Hence, the water is increasing and the derivative of the volume is +.')

            elif state['V']['derivative'] == '-':
                print(' - The inflow and outflow are both influencing the volume, but in this case the outflow is stronger than the inflow.\n'
                    '   Hence, the water is decreasing and the derivative of the volume is -.')

            else:
                print(' - The inflow and outflow are both influencing the volume, but in this case the inflow is as strong as the outflow.\n'
                    '   Hence, the water is stable (the amount of water coming in is equal to the amount of water flowing out) and the derivative \n'
                    '   of the volume is 0.')

        # show the proportionalities
        if len(self.quantities) > 3:
            print(' - The proportionality between volume, outflow, height and pressure cause the derivatives to be the same.')
        else:
            print(' - The proportionality between volume and outflow cause the derivatives to be the same.')

        return

    def inter_trace(self, curr_state, next_state):
        """
        This function shows the inter state trace, to help the user understand how and why a certain transition between
        states is valid
        :return:
        """

        s = "Q | M   D          Q | M   D\n--+------          --+------\n"
        for i, (quan, values) in enumerate(curr_state.items()):
            if quan == 'V':
                s += "{} | {:4s}{}  ---->   {} | {:4s}{}\n" \
                    .format(quan, values['magnitude'], values['derivative'],
                            quan, next_state[quan]['magnitude'], next_state[quan]['derivative'])
            else:
                s += "{} | {:4s}{}          {} | {:4s}{}\n" \
                    .format(quan, values['magnitude'], values['derivative'],
                            quan, next_state[quan]['magnitude'], next_state[quan]['derivative'])

        print(s)

        ################
        # Inter states #
        ################

        print('INTER-state trace:')
        print()

        # Exogenous actions

        # check the inflow derivative change
        # get derivative indices
        curr_der_ind = self.derivatives.index(curr_state['I']['derivative'])
        next_der_ind = self.derivatives.index(next_state['I']['derivative'])
        next_mag = next_state['I']['magnitude']

        # check if inflow will be empty
        if next_mag == '0' and curr_der_ind != next_der_ind:
            print(' - In this transition the inflow has decreased to the point where the tap is fully closed.')
        elif curr_der_ind < next_der_ind and next_der_ind != 1:
            print(
                ' - In this transition a user performs an exogenous action where the inflow starts increasing by further opening up the tap')
        elif next_der_ind < curr_der_ind and next_der_ind != 1:
            print(
                ' - In this transition a user performs an exogenous action where the inflow starts decreasing by closing up the tap')
        elif curr_der_ind < next_der_ind:
            print(
                ' - In this transition a user performs an exogenous action where the inflow stops decreasing by further opening up the tap.')
        elif next_der_ind < curr_der_ind:
            print(
                ' - In this transition a user performs an exogenous action where the inflow stops increasing by closing up the tap.')
        else:
            print(' - No exogenous action is performed')

        # derivative
        # check for changes in magnitude
        for quantity in self.quantities:
            if curr_state[quantity]['magnitude'] != next_state[quantity]['magnitude']:
                print(' - The magnitude of {} is changed from {} to {}, due to a derivative of {}' \
                      .format(quantity, curr_state[quantity]['magnitude'], next_state[quantity]['magnitude'],
                              curr_state[quantity]['derivative']))

        if curr_state['V']['derivative'] == '-' \
                and curr_state[quantity]['magnitude'] != next_state[quantity]['magnitude']:
            print()
            print(
                '  *** The derivative is negative so the water is flowing out of the tub, hence magnitude decreases ***')
        elif curr_state['V']['derivative'] == '+' \
                and curr_state[quantity]['magnitude'] != next_state[quantity]['magnitude']:
            print()
            print(
                '  *** The derivative is positive so the water is flowing into the tub, hence magnitude increases ***')

        if curr_state['V']['magnitude'] != next_state['V']['magnitude']:
            if next_state['V']['magnitude'] == 'max' and next_state['V']['derivative'] == '0':
                print()
                print(
                    '  *** The derivatives change to 0 because the bath is already full and thus the volume can not keep increasing ***')
            elif next_state['V']['magnitude'] == 'max':
                print()
                print(
                    '  *** The derivatives change to - because once the bath is full the outflow is stronger than the inflow\n'
                    '      and thus the volume will start decreasing ***')


            elif next_state['V']['magnitude'] == '0' and next_state['V']['derivative'] == '0':
                print()
                print(
                    '  *** The derivatives change to 0 because the bath is already empty and thus the volume can not keep decreasing ***')
            elif next_state['V']['magnitude'] == '0':
                print()
                print(
                    '  *** The derivatives change to + because once the bath is empty there is no longer any outflow.\n'
                    '      Hence, the inflow becomes the only influence on the volume and th volume will start increasing ***')
        else:
            if curr_state['V']['derivative'] == '+' and\
                    (curr_state['V']['magnitude'] != 'max' or curr_state['V']['magnitude'] != '0'):
                print(' - While the magnitude remains the same, the amount of water is increasing. Due to the fact that the magnitude\n'
                      '   of + is an interval, this does not become apparent in the magnitude, while it is indeed actually happening.')

            elif curr_state['V']['derivative'] == '-':
                print(' - While the magnitude remains the same, the amount of water is decreasing. Due to the fact that the magnitude\n'
                    '   of + is an interval, this does not become apparent in the magnitude, while it is indeed actually happening.')

            else:
                if len(self.quantities) > 3:
                    print(' - The amount of water in the tub remains the same, so no changes for volume, outflow, height or pressure.')
                else:
                    print(' - The amount of water in the tub remains the same, so no changes for volume or outflow.')

        return


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

    if ARGS.extended:
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

    # create model
    model = QRModel(quantities, derivatives, props, influences, value_correspondence)

    # generate and filter all states
    states = model.gen_states()
    filtered_states = model.vc_filter()

    # get all valid states to create nodes
    valid_states, all_derivs = model.valid_state(filtered_states)

    nodename = {}

    transitions = defaultdict(list)

    node_ID = {}

    letter = 65 #ascii

    for state in valid_states:

        # create node 'name'
        s = "Q | M   D\n--+------\n"
        for quan, values in state.items():
            s += "{} | {:4s}{}\n".format(quan, values['magnitude'], values['derivative'])
        nodename[str(state)] = s

        # get all transitions
        next_states = model.transition_states(state)

        # store all transitions
        for next_state in next_states:
            transitions[str(state)].append(str(next_state))

        node_ID[str(state)] = chr(letter)
        letter += 1 

    # generate trace
    if ARGS.trace:
        # loop through valid states
        for state in valid_states:
            # generate the intra state trace and the inter state trace between this state and all its transitions
            model.gen_trace(state, all_derivs, nodename)

        print('Number of states before pruning: {}'.format(len(model.all_states)))
        print('Number of states after pruning: {}'.format(len(model.valid_states)))

    ######################
    # Create state graph #
    ######################

    total_length = 0
    for state_list in transitions.values():

        list2 = list(set(state_list))
        total_length += len(list2)

    dot = Digraph('unix', filename='stategraph.gv')

    dot.node_attr.update(color='lightblue2', style='filled', shape='box', fontsize='20', fontname='Helvetica', height='0', width='0')
    dot.edge_attr.update(arrowhead='vee', arrowsize='1', arrowtail="both")

    edges_graph = []

    for key, name in nodename.items():

        dot.node(node_ID[key], name)

        for trans in transitions[key]:
            edges_graph.append(node_ID[key] + node_ID[trans])

    edges_graph = list(set(edges_graph))

    dot.edges(edges_graph)
    dot.edge('B', 'H', constraint='false')

    if ARGS.trace:
        print('Number of transitions: {}'.format(len(edges_graph)))

    if ARGS.graph:
        dot.view()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--extended', default=0, type=int,
                        help="Run algorithm on extended system")
    parser.add_argument('--graph', default=1, type=int,
                        help='Ask algorithm to create the state graph')
    parser.add_argument('--trace', default=1, type=int,
                        help='Ask algorithm to leave a trace')

    ARGS = parser.parse_args()

    main()

