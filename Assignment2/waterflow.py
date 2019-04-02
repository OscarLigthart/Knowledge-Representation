import itertools

# Start by generating all possible states for Inflow, Outflow and Volume

# Quantity spaces:
# inflow [0,+]
# outflow [0,+,max]
# derivatives [-,0,+]

quantities = {
    'I': ['0', '+'],
    'V': ['0', '+', 'max'],
    'O': ['0', '+', 'max'],
}

derivatives = ['-', '0', '+']

all_permutations = [quantities['I'], quantities['V'], quantities['O'], derivatives, derivatives, derivatives]

pre_states = list(itertools.product(*all_permutations))
print(pre_states)
print(len(pre_states))

states = []
# order the states --> two lists where one is magnitude and the other is derivative
for state in pre_states:
    new_state = {}
    for i, key in enumerate(quantities.keys()):
        new_state[key] = {}
        new_state[key]['magnitude'] = state[i]
        new_state[key]['derivative'] = state[3+i]
    states.append(new_state)

# introduce dependencies
# I --(I+)--> V
# O --(I-)--> V
# V --(P+)--> O

# get beginning state, find states that fit the dependencies?
# what is the beginning state?
# start with an empty tub and open the tap

# for every state get the 

# find new way to save data
# how to save data?








# introduce value correspondences

# use these to check which states are possible and which aren't