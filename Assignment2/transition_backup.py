

def transition_states(self, curr_state, exogenous=True):
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
                            text += '{} gets a magnitude of {}, due to the previous magnitude of {} having' \
                                    ' a derivative of {}\n' \
                                .format(quan, new_state[quan]['magnitude'],
                                        curr_state[quan]['magnitude'], curr_state[quan]['derivative'])
                            val = True

                    if val:
                        self.trace[str(curr_state) + str(new_state)]['inter'] = sample_text + text

                    else:
                        if curr_state['I']['derivative'] == '+':
                            # here the trace that inflow is getting stronger
                            self.trace[str(curr_state) + str(new_state)]['inter'] = \
                                'The inflow is getting stronger compared to the outflow ' \
                                'so the derivative of V changes from {} to {}' \
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
        # instead: FOLLOW DERIVATIVE CHANGES
        else:
            # todo: follow derivative changes --> what to do with derivative then? --> keep it, set it to 0 if landmark

            # get the index of the current magnitude
            # ind = self.quantities[quantity].index(mag)
            #
            # if der == '+':
            #     new_mag = self.quantities[quantity][ind + 1]
            #
            #     if new_mag == 'max' or new_mag == '0':
            #         new_der = '0'
            #     else:
            #         new_der = der
            #
            # elif der == '-':
            #     new_mag = self.quantities[quantity][ind - 1]
            #
            #     if new_mag == 'max' or new_mag == '0':
            #         new_der = '0'
            #     else:
            #         new_der = der
            #
            # else:
            #     new_mag = mag
            #     new_der = der
            #
            # subs[quantity].append({'magnitude': new_mag, 'derivative': new_der})

            # OLD CODE
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

                transition_states.append(new_state)

                #######################################
                # Leave a trace for exogenous actions #
                #######################################
                if self.leave_trace:
                    if self.valid_state([new_state]):
                        # trace:
                        self.trace[str(curr_state) + str(new_state)]['inter'] = \
                            'This state is a result of an exogenous action, ' \
                            'where a person manually operates the inflow.'

    # now we have all the possible transitions from a single state!
    transition_states = self.valid_state(transition_states, curr_state)

    # remove states that have only influence changes --> if the derivative of the others is not 0

    for state in transition_states:
        check = True

        # inflow can change so long as all other magnitudes are landmarks or
        # the same
        if curr_state['I']['magnitude'] != state["I"]['magnitude']:
            if curr_state['V']['magnitude'] != state['V']['magnitude']:
                check = False

        # if inflow magnitude is 0, next state volume can't be max
        if curr_state['I']['magnitude'] == '0' and state['V']['magnitude'] == 'max':
            check = False

        # if inflow derivative is positive, volume derivative can't be negative in next state
        if curr_state['I']['derivative'] == '+' and state['V']['derivative'] == '-':
            check = False
        if curr_state['I']['derivative'] == '-' and state['V']['derivative'] == '+':
            check = False

        # if inflow magnitude is zero and volume is max, no transition to other max

        #

        if not check:
            # check if valid over here
            transition_states.remove(state)