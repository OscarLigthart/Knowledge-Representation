import plot_data
from plot_data import *
import matplotlib

#####################################
########## PLOT MOM DATA ############
#####################################

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

matplotlib.rc('xtick', labelsize=13)
matplotlib.rc('ytick', labelsize=12)


MOM_data_to_plot = get_data_to_plot("splits", MOM_data_files)
names = list(MOM_data_to_plot.keys())
values = [value["data"] for value in MOM_data_to_plot.values()]
print(values)
std = [value["std"] for value in MOM_data_to_plot.values()]


plt.plot(names, values, marker = 'o', label='MOMS')

MOM_data_to_plot = get_data_to_plot("splits", MOM_pairs_files)
values = [value["data"] for value in MOM_data_to_plot.values()]
print(values)
std = [value["std"] for value in MOM_data_to_plot.values()]


plt.plot(names, values, marker = 'o', label='MOMS + Naked-pairs')

MOM_data_to_plot = get_data_to_plot("splits", MOM_triples_files)
values = [value["data"] for value in MOM_data_to_plot.values()]
std = [value["std"] for value in MOM_data_to_plot.values()]


plt.plot(names, values, marker = 'o', label='MOMS + Naked-triples')

MOM_data_to_plot = get_data_to_plot("splits", MOM_x_wing_files)
values = [value["data"] for value in MOM_data_to_plot.values()]
std = [value["std"] for value in MOM_data_to_plot.values()]


plt.plot(names, values, marker = 'o', label='MOMS + x-wing')

MOM_data_to_plot = get_data_to_plot("splits", MOM_all_files)
values = [value["data"] for value in MOM_data_to_plot.values()]
std = [value["std"] for value in MOM_data_to_plot.values()]


plt.plot(names, values, marker = 'o', label='MOMS + all')

plt.ylabel('Splits', fontsize=12)
plt.xlabel('Sudoku level', fontsize=12)
plt.legend(prop={'size': 12})
plt.savefig('report_images/MOM-heuristics')
plt.show()

##################################
########## PLOT JW DATA ##########
##################################

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

JW_data_to_plot = get_data_to_plot("splits", JW_data_files)
names = list(MOM_data_to_plot.keys())
values = [value["data"] for value in JW_data_to_plot.values()]
print(values)
std = [value["std"] for value in JW_data_to_plot.values()]


plt.plot(names, values, marker='o', label='JW')

JW_data_to_plot = get_data_to_plot("splits", JW_pairs_files)
values = [value["data"] for value in JW_data_to_plot.values()]
print(values)
std = [value["std"] for value in JW_data_to_plot.values()]


plt.plot(names, values, marker='o', label='JW + Naked-pairs')

JW_data_to_plot = get_data_to_plot("splits", JW_triples_files)
values = [value["data"] for value in JW_data_to_plot.values()]
std = [value["std"] for value in JW_data_to_plot.values()]


plt.plot(names, values, marker='o', label='JW + Naked-triples')

JW_data_to_plot = get_data_to_plot("splits", JW_x_wing_files)
values = [value["data"] for value in JW_data_to_plot.values()]
std = [value["std"] for value in JW_data_to_plot.values()]


plt.plot(names, values, marker='o', label='JW + x-wing')

JW_data_to_plot = get_data_to_plot("splits", JW_all_files)
values = [value["data"] for value in JW_data_to_plot.values()]
std = [value["std"] for value in JW_data_to_plot.values()]


plt.plot(names, values, marker='o', label='JW + all')

plt.ylabel('Splits', fontsize=12)
plt.xlabel('Sudoku level', fontsize=12)
plt.legend(prop={'size': 12})
plt.savefig('report_images/JW-heuristics')
plt.show()

