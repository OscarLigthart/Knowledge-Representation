import itertools
from collections import defaultdict

class QRModel:
    def __init__(self, quantities, derivatives, proportionality, influence, value_correspondences):
        self.quantities = quantities
        self.derivatives = derivatives
        self.vc = value_correspondences
        self.proportionality = proportionality
        self.influence = influence
        self.landmarks = {
            q: [v[i] for i in range(len(v)) if i % 2 == 0]
            for q, v in quantities.items()
        }

    def gen_states(self):

        """Generate all possible states"""

        all_permutations = [self.quantities['I'], self.quantities['V'], self.quantities['O'],
                            self.derivatives, self.derivatives, self.derivatives]

        pre_states = list(itertools.product(*all_permutations))

        states = []
        # order the states --> two lists where one is magnitude and the other is derivative
        for state in pre_states:
            new_state = {}
            for i, key in enumerate(self.quantities.keys()):
                new_state[key] = {}
                new_state[key]['magnitude'] = state[i]
                new_state[key]['derivative'] = state[3 + i]
            states.append(new_state)

        self.all_states = states
        return states

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


    def transition_states(self, curr_state):
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
                # change it in both directions
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
                for derivative in self.derivatives:
                    subs[quantity].append({'magnitude': new_mag, 'derivative': derivative})

        print(subs)
        print(len(subs))

        transition_states = []

        for perm in itertools.product(*subs.values()):

            # Create a new state object
            new_state = {}
            for i, quantity in enumerate(self.quantities):
                new_state[quantity] = perm[i]

            # check if the generated state is among the filtered (possible) states
            if new_state in self.filtered_states and new_state != curr_state:
                transition_states.append(new_state)

        # now we have all the possible transitions from a single state!

        print('current state:')
        print(curr_state)
        print('possible transitions:')
        print(transition_states)
        print(len(transition_states))
        transition_states = self.valid_state(transition_states, curr_state)

        return transition_states

    def valid_state(self, states, curr_state):
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

            # test_state = {'I': {'magnitude': '+', 'derivative': '+'}, 'O': {'magnitude': '0', 'derivative': '+'},
            # 'V': {'magnitude': '0', 'derivative': '+'}}

            #test_state = {'I': {'magnitude': '0', 'derivative': '0'}, 'O': {'magnitude': '0', 'derivative': '+'},
            #              'V': {'magnitude': '+', 'derivative': '+'}}


            # todo it now works for for everything except ambiguous states

            check = self.find_proportionality(state)

            derivs = self.find_influence(state)

            # check if all proportionalities are satisfied, then use the calculus rules to determine whether ambiguity
            # occurs
            # todo: softcode
            if all(check):

                # check for all zeros
                if all([x == 0 for x in derivs['V']]):
                    #print('Derivative should be 0 as there is no effect')
                    # check whether derivative actually is 0
                    if state['V']['derivative'] == '0':
                        valid_states.append(state)

                # sum and check if positive or negative
                elif sum(derivs['V']) > 0:
                    #print('Derivative should be positive')
                    # check whether the derivative actually is positive
                    if state['V']['derivative'] == '+':
                        valid_states.append(state)

                elif sum(derivs['V']) < 0:
                    #print('Derivative should be negative')
                    # check whether the derivative actually is negative
                    if state['V']['derivative'] == '-':
                        valid_states.append(state)

                # sum and check if 0
                elif sum(derivs['V']) == 0:
                    #print('Ambiguous')
                    # return state with all derivatives
                    valid_states.append(state)

                #####################
                # Exogenous actions #
                #####################

                # allow for changes in inflow when? not always --> proportionality should be true
                # every value should be the same as the old state, except for the change in derivative for the inflow
                # that could also validate a state

                # check if all but the inflow is the same as the old state --> change the inflow in a
                # neighbouring direction

                valid = [False for x in range(len(self.quantities))]
                for j, quantity in enumerate(self.quantities):
                    if quantity == 'I':
                        if state[quantity]['magnitude'] == curr_state[quantity]['magnitude']:
                            # now check if difference between curr state derivative is just one compared to next state
                            # get both indices and subtract, should be no more than 1
                            ind1 = self.derivatives.index(state[quantity]['derivative'])
                            print(ind1)
                            ind2 = self.derivatives.index(curr_state[quantity]['derivative'])
                            print(ind2)

                            if abs(ind1 - ind2) < 2:
                                valid[j] = True

                    else:
                        if state[quantity] == curr_state[quantity]:
                            valid[j] = True

                if all(valid) and state not in valid_states:
                    valid_states.append(state)

        print('states')
        print(valid_states)

        # --> can both effect the derivatives of states so create the matrix

        # todo: check for ambiguity --> if there exists a positive and negative influence/prop effect, derivative can
        # todo: be -, 0, + all together



        # todo: transition direction --> Outflow can get stronger when inflow is decreasing and Inflow can get stronger
        # todo: when it is increasing

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
                if state[quantity1]['derivative'] == state[quantity2]['derivative']:
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


# use the dependencies to find following states
def dependencies(state, all_states):

    # everything should be the same except for the influence, proportionality for a state to be able to transition
    # into another state
    transitions = []

        # inflow influence
    for compare_state in all_states:
        if state['I']['magnitude'] == '+':
            if compare_state['V']['derivative'] == '+':
                transitions.append(compare_state)

        # outflow influence
        if state['O']['magnitude'] == '+':
            if compare_state['V']['derivative'] == '+':
                transitions.append(compare_state)

    # volume proportionality



    return None


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

    model = QRModel(quantities, derivatives, props, influences, value_correspondence)
    states = model.gen_states()
    filtered_states = model.vc_filter()

    #test_state = {'I': {'magnitude': }}

    transitions = model.transition_states(filtered_states[0])
    #print(transitions)

    trans2 = model.transition_states(transitions[0])
    print(trans2)

    trans3 = model.transition_states(trans2[-1])
    print(len(trans3))
    print()
    for tr in trans3:
        print(tr)
        print()




main()
