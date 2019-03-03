from scipy.stats import stats
from plot_data import *

#################
# MOM HEURISTIC #
#################

MOM_data_files = {"simple": "data/MOM_simple.p",
                  "easy": "data/MOM_easy.p",
                  "intermediate": "data/MOM_intermediate.p",
                  "expert": "data/MOM_expert.p"}

MOM_pairs_files = {"simple": "data/MOM-2-naked-pairs_simple.p",
                      "easy": "data/MOM-2-naked-pairs_easy.p",
                      "intermediate": "data/MOM-2-naked-pairs_intermediate.p",
                      "expert": "data/MOM-2-naked-pairs_expert.p"}

MOM_triples_files = {"simple": "data/MOM-2-naked-triples_simple.p",
                      "easy": "data/MOM-2-naked-triples_easy.p",
                      "intermediate": "data/MOM-2-naked-triples_intermediate.p",
                      "expert": "data/MOM-2-naked-triples_expert.p"}

MOM_x_wing_files = {"simple": "data/MOM-2-x-wing_simple.p",
                      "easy": "data/MOM-2-x-wing_easy.p",
                      "intermediate": "data/MOM-2-x-wing_intermediate.p",
                    "expert": "data/MOM-2-x-wing_expert.p"}

MOM_all_files = {"simple": "data/MOM-all_simple.p",
                      "easy": "data/MOM-all_easy.p",
                      "intermediate": "data/MOM-all_intermediate.p",
                    "expert": "data/MOM-all_expert.p"}

print("--------------------------------")
print("--- REMOVED LITERALS FOR MOM ---")
print("--------------------------------")
print()

# BASELINE
MOM_data_to_plot = refactor_data(MOM_data_files)
names = list(MOM_data_to_plot.keys())
normal_splits = [value["splits"]["all"] for value in MOM_data_to_plot.values()]

# ALL STRATEGIES
MOM_data_to_plot = refactor_data(MOM_all_files)
all_splits = [value["splits"]["all"] for value in MOM_data_to_plot.values()]

# NAKED PAIRS
MOM_data_to_plot = refactor_data(MOM_pairs_files)

naked_pairs = [value["nr-naked-pairs"] for value in MOM_data_to_plot.values()]
naked_pairs_removed = [value["naked-pairs-removed"] for value in MOM_data_to_plot.values()]
pairs_splits = [value["splits"]["all"] for value in MOM_data_to_plot.values()]
print('Amount of naked pairs:')
print(naked_pairs)

print('Amount of literals removed due to naked-pairs:')
print(naked_pairs_removed)
print()

# NAKED TRIPLES
MOM_data_to_plot = refactor_data(MOM_triples_files)
naked_triples = [value["nr-naked-triples"] for value in MOM_data_to_plot.values()]
naked_triples_removed = [value["naked-triples-removed"] for value in MOM_data_to_plot.values()]
triple_splits = [value["splits"]["all"] for value in MOM_data_to_plot.values()]

print('Amount of naked triples:')
print(naked_triples)

print('Amount of literals removed due to naked-triples:')
print(naked_triples_removed)
print()

# X-WINGS
MOM_data_to_plot = refactor_data(MOM_x_wing_files)
x_wings = [value["x-wings"] for value in MOM_data_to_plot.values()]
x_removed = [value["x-removed"] for value in MOM_data_to_plot.values()]
x_splits = [value["splits"]["all"] for value in MOM_data_to_plot.values()]

print('Amount of x-wings:')
print(x_wings)

print('Amount of literals removed due to x-wings:')
print(x_removed)
print()


print()
print("------------------------------------------")
print("------ STATISTICS FOR MOM HEURISTIC ------")
print("------------------------------------------")
print()

difficulty = ["Simple", "Easy", "Intermediate", "Expert"]
# statistics
for d in range(4):
    print()
    print("Testing for difficulty: " + difficulty[d])

    print('T-test for baseline vs. naked-pairs:')
    x = stats.ttest_ind(normal_splits[d], pairs_splits[d])
    print(x)

    print('T-test for baseline vs. naked-triples:')
    x = stats.ttest_ind(normal_splits[d], triple_splits[d])
    print(x)

    print('T-test for baseline vs. x-wing:')
    x = stats.ttest_ind(normal_splits[d], x_splits[d])
    print(x)

    print('T-test for baseline vs. all:')
    x = stats.ttest_ind(normal_splits[d], all_splits[d])
    print(x)





################
# JW HEURISTIC #
################

JW_data_files = {"simple": "data/JW_simple.p",
                  "easy": "data/JW_easy.p",
                  "intermediate": "data/JW_intermediate.p",
                  "expert": "data/JW_expert.p"}

JW_pairs_files = {"simple": "data/JW-naked-pairs_simple.p",
                      "easy": "data/JW-naked-pairs_easy.p",
                      "intermediate": "data/JW-naked-pairs_intermediate.p",
                      "expert": "data/JW-naked-pairs_expert.p"}

JW_triples_files = {"simple": "data/JW-naked-triples_simple.p",
                      "easy": "data/JW-naked-triples_easy.p",
                      "intermediate": "data/JW-naked-triples_intermediate.p",
                      "expert": "data/JW-naked-triples_expert.p"}

JW_x_wing_files = {"simple": "data/JW-x-wing_simple.p",
                      "easy": "data/JW-x-wing_easy.p",
                      "intermediate": "data/JW-x-wing_intermediate.p",
                    "expert": "data/JW-x-wing_expert.p"}

JW_all_files = {"simple": "data/JW-all_simple.p",
                      "easy": "data/JW-all_easy.p",
                      "intermediate": "data/JW-all_intermediate.p",
                    "expert": "data/JW-all_expert.p"}

print("--------------------------------")
print("--- REMOVED LITERALS FOR JW ----")
print("--------------------------------")
print()


# BASELINE
JW_data_to_plot = refactor_data(JW_data_files)
names = list(JW_data_to_plot.keys())
normal_splits = [value["splits"]["all"] for value in JW_data_to_plot.values()]

# ALL STRATEGIES
JW_data_to_plot = refactor_data(JW_all_files)
all_splits = [value["splits"]["all"] for value in JW_data_to_plot.values()]

# NAKED PAIRS
JW_data_to_plot = refactor_data(JW_pairs_files)
naked_pairs = [value["nr-naked-pairs"] for value in JW_data_to_plot.values()]
naked_pairs_removed = [value["naked-pairs-removed"] for value in JW_data_to_plot.values()]
pairs_splits = [value["splits"]["all"] for value in JW_data_to_plot.values()]

print('Amount of naked pairs:')
print(naked_pairs)

print('Amount of literals removed due to naked-pairs:')
print(naked_pairs_removed)
print()

# NAKED TRIPLES
JW_data_to_plot = refactor_data(JW_triples_files)
naked_triples = [value["nr-naked-triples"] for value in JW_data_to_plot.values()]
naked_triples_removed = [value["naked-triples-removed"] for value in JW_data_to_plot.values()]
triple_splits = [value["splits"]["all"] for value in JW_data_to_plot.values()]

print('Amount of naked triples:')
print(naked_triples)

print('Amount of literals removed due to naked-triples:')
print(naked_triples_removed)
print()

# X-WINGS
JW_data_to_plot = refactor_data(JW_x_wing_files)
x_wings = [value["x-wings"] for value in JW_data_to_plot.values()]
x_removed = [value["x-removed"] for value in JW_data_to_plot.values()]
x_splits = [value["splits"]["all"] for value in JW_data_to_plot.values()]

print('Amount of x-wings:')
print(x_wings)

print('Amount of literals removed due to x-wings:')
print(x_removed)
print()

print()
print("------------------------------------------")
print("------ STATISTICS FOR JW HEURISTIC -------")
print("------------------------------------------")
print()

difficulty = ["Simple", "Easy", "Intermediate", "Expert"]
# statistics
for d in range(4):
    print()
    print("Testing for difficulty: " + difficulty[d])

    print('T-test for baseline vs. naked-pairs:')
    x = stats.ttest_ind(normal_splits[d], pairs_splits[d])
    print(x)

    print('T-test for baseline vs. naked-triples:')
    x = stats.ttest_ind(normal_splits[d], triple_splits[d])
    print(x)

    print('T-test for baseline vs. x-wing:')
    x = stats.ttest_ind(normal_splits[d], x_splits[d])
    print(x)

    print('T-test for baseline vs. all:')
    x = stats.ttest_ind(normal_splits[d], all_splits[d])
    print(x)

