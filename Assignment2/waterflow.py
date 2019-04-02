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

all_permutations = [quantities['I'], derivatives, quantities['V'], derivatives, quantities['O'], derivatives]

pre_states = list(itertools.product(*all_permutations))
print(pre_states)
print(len(pre_states))

states = []
# order the states --> two lists where one is magnitude and the other is derivative
for state in pre_states:
    magnitudes = []
    d = []
    for i, value in enumerate(state):
        if i % 2 == 0:
            magnitudes.append(value)
        else:
            d.append(value)

    states.append([magnitudes, d])

print(states)

# introduce dependencies
# I --(I+)--> V
# O --(I-)--> V
# V --(P+)--> O

# get beginning state, find states that fit the dependencies?





# introduce value correspondences

# use these to check which states are possible and which aren't