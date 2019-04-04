import itertools

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
        Determine which states a certain state can transition to based on the derivatives
        :return:
        """

        transition_states = []

        # for a transition to be possible we need: same values, changed values based on derivative
        # check all derivatives and find next quantity for these derivatives
        # all derivatives need to be satisfied at once for a state to be candidate for a valid transition

        ###################################################################
        # First get changes in magnitude on the account of the derivative #
        ###################################################################

        quan_trans = {}
        for quantity, values in curr_state.items():
            mag = values['magnitude']
            der = values['derivative']

            # get the index of the current magnitude
            ind = self.quantities[quantity].index(mag)

            # magnitude has to change according to the derivative
            # if derivative is 0, magnitude will not change

            # reduce the magnitude by 1 if the derivative is negative
            if der == '-':
                new_mag = self.quantities[quantity][ind - 1]

            # increase the magnitude by 1 if the derivative is positive
            elif der == '+':
                if quantity == 'I':
                    new_mag = self.quantities[quantity][min(1, ind + 1)]
                else:
                    new_mag = self.quantities[quantity][ind + 1]

            # if the derivative is 0, keep the old magnitude
            else:
                new_mag = mag

            # save the new possible magnitude for all quantities
            quan_trans[quantity] = new_mag

        print(quan_trans)
        # works!
        #########################
        # Get transition states #
        #########################

        # loop through all filtered states to check for possible transitions
        for state in self.filtered_states:

            # set transition to false until proven otherwise
            valid = False

            check = [False for x in range(len(state))]
            # derivative has to remain the same, except when new magnitude is a landmark
            for i, (quantity, values) in enumerate(state.items()):


                # check if magnitude is the new magnitude for all states
                if values['magnitude'] == quan_trans[quantity]:
                    # check if derivative remains the same (except for when on landmark, then derivative can be 0)
                    # todo: later on --> combine this with influence and proportionality using matrices


                    if values['derivative'] == curr_state[quantity]['derivative'] or \
                            values['derivative'] == '0' and \
                            (quan_trans[quantity] == '0' or quan_trans[quantity] == 'max'):
                        check[i] = True

                    # has to be true for all values
                    # check if all derivatives are same
                    #
                    # if values['derivative'] == curr_state[quantity]['derivative']:
                    #     check[i] = True

                # if all derivatives are the same,
                if all(check):
                    # todo leave trace that state transition is due to derivative
                    valid = True

            # derivative of the inflow can change only when every other value remains the same
            if state['V'] == curr_state['V'] and state['O'] == curr_state['O'] and \
                    state['I']['magnitude'] == curr_state['I']['magnitude']:
                # derivative can only change by one in either direction

                # find the index of current derivative of inflow
                ind = self.derivatives.index(curr_state['I']['derivative'])

                # find possible derivative transitions
                ders = self.derivatives[max(0, ind-1): min(3, ind+2)]

                if len(ders) == 1:
                    ders = [ders]

                # for all of these derivatives, add the states
                if state['I']['derivative'] in ders:
                    valid = True

            if valid and state != curr_state:
                transition_states.append(state)
                # todo leave trace that state transition is due to exogenous activity

        # seems to work!

        # find transition states that work according to current state?
        # or take the next states and apply the influences and proportionality

        # if something changes, check it again?
        for state in transition_states:

            self.find_influence(curr_state, state)

            self.find_proportionality(curr_state, state)




        # add the effects of proportionality and influence

        # create the matrix of effects on derivatives

        # take all states that are found in this matrix

        return transition_states

    def find_proportionality(self, curr_state, next_state):

        # find where proportionalities occur
        props = self.proportionality

        # for every proportional relation, find states that follow these rules
        for prop in props:
            pass

        return None

    def find_influence(self, curr_state, next_state):

        influences = self.influence

        for inf in influences:
            quantity1 = inf[0]
            relation = inf[1]
            quantity2 = inf[2]

            if curr_state[quantity1] != '0':
                if relation == 'I+':
                    # take all next states that are equal apart from this bit?
                    pass
                elif relation == 'I-':
                    pass


            # if quantity 1 is positive, the derivative of quantity 2 has to be positive as well

        return None

    def valid_state(self):
        """
        Check whether state is valid based on proportionality and influence rules and filter those that are not from
        the transition tree
        :return:
        """

        return None





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
    print(transitions)
    print(len(transitions))

    trans2 = model.transition_states(transitions[0])

    print(trans2)

    trans3 = model.transition_states(trans2[1])

    print(trans3)


main()
