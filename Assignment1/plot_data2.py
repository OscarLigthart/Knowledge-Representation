import matplotlib.pyplot as plt
import pickle
import numpy as np
import matplotlib
from scipy.stats import stats


def main():

    DP_data_files = {"simple": "data/DP_conc_simple.p",
                    "easy": "data/DP_conc_easy.p",
                    "intermediate": "data/DP_100_intermediate.p",
                    "expert": "data/DP_100_expert.p"}

    JW_data_files = {"simple": "data/JW_simple.p",
                  "easy": "data/JW_easy.p",
                  "intermediate": "data/JW_intermediate.p",
                  "expert": "data/JW_expert.p"}

    MOM_data_files = {"simple": "data/MOM-2_simple.p",
                     "easy": "data/MOM-2_easy.p",
                     "intermediate": "data/MOM-2_intermediate.p",
                     "expert": "data/MOM-2_expert.p"}

    matplotlib.rc('xtick', labelsize=13)
    matplotlib.rc('ytick', labelsize=12)

    DP_data_to_plot = get_data_to_plot("splits", DP_data_files)
    DP_data2 = refactor_data(DP_data_files)
    DP_names = list(DP_data_to_plot.keys())
    DP_values = np.array([value["data"] for value in DP_data_to_plot.values()])
    DP_splits = [value["splits"]["all"] for value in DP_data2.values()]
    std = np.array([value["std"] for value in DP_data_to_plot.values()])

    print(std)




    plt.plot(DP_names, DP_values, marker = 'o', label='DP')
    plt.fill_between(DP_names, DP_values-std, DP_values + std, facecolor='blue',alpha=0.075, interpolate=True)



    JW_data_to_plot = get_data_to_plot("splits", JW_data_files)
    JW_data2 = refactor_data(JW_data_files)
    JW_names = list(JW_data_to_plot.keys())
    JW_values = [value["data"] for value in JW_data_to_plot.values()]
    JW_std = [value["std"] for value in JW_data_to_plot.values()]
    JW_splits = [value["splits"]["all"] for value in JW_data2.values()]
    plt.plot(JW_names, JW_values,  marker = 'o', label='JW')


    MOM_data_to_plot = get_data_to_plot("splits", MOM_data_files)
    MOM_data2 = refactor_data(MOM_data_files)
    MOM_names = list(MOM_data_to_plot.keys())
    MOM_values = [value["data"] for value in MOM_data_to_plot.values()]
    MOM_std = [value["std"] for value in MOM_data_to_plot.values()]
    MOM_splits = [value["splits"]["all"] for value in MOM_data2.values()]
    plt.plot(MOM_names, MOM_values,  marker = 'o', label='MOMS')


    plt.ylabel('Splits')
    plt.xlabel('Sudoku level', fontsize=12)
    plt.ylabel('Splits', fontsize=12)
    plt.legend(prop={'size': 12})
    #plt.errorbar(DP_names, DP_values, std, ecolor="#b3b3b3", capsize=3, elinewidth=0.6)

    plt.savefig('report_images/SAT-heuristics')
    plt.show()

    difficulty = ["Simple", "Easy", "Intermediate", "Expert"]
    # statistics
    for d in range(4):
        print()
        print("Testing for difficulty: " + difficulty[d])

        print('T-test for DP vs. MOM:')
        x = stats.ttest_ind(DP_splits[d], MOM_splits[d])
        print(x)

        print('T-test for DP vs. JW:')
        x = stats.ttest_ind(DP_splits[d], JW_splits[d])
        print(x)

        print('T-test for JW vs. MOM:')
        x = stats.ttest_ind(JW_splits[d], MOM_splits[d])
        print(x)


    difficulty = ["Simple", "Easy", "Intermediate", "Expert"]
    # statistics
    for d in range(3):
        print()
        print("Testing for difficulty: " + difficulty[d] + " vs. "+ difficulty[d+1])

        print('T-test for DP:')
        x = stats.ttest_ind(DP_splits[d], DP_splits[d+1])
        print(x)

        print('T-test for JW:')
        x = stats.ttest_ind(JW_splits[d], JW_splits[d+1])
        print(x)

        print('T-test for MOM:')
        x = stats.ttest_ind(MOM_splits[d], MOM_splits[d+1])
        print(x)




    #
    # # grouped bar plot
    #
    # N = 4
    # fig, ax = plt.subplots()
    #
    # ind = np.arange(N)  # the x locations for the groups
    # width = 0.2  # the width of the bars
    #
    #
    # DP_data_to_plot = get_data_to_plot("splits", DP_data_files)
    # DP_values = [value["data"] for value in DP_data_to_plot.values()]
    # DP_std = [value["std"] for value in DP_data_to_plot.values()]
    #
    # p1 = ax.bar(ind-0.13, DP_values, width, yerr=DP_std, bottom = -0.5)
    #
    # JW_data_to_plot = get_data_to_plot("splits", JW_data_files)
    # JW_values = [value["data"] for value in JW_data_to_plot.values()]
    # JW_std = [value["std"] for value in JW_data_to_plot.values()]
    #
    # p2 = ax.bar(ind + width-0.13, JW_values, width, yerr=JW_std, bottom = -0.5)
    #
    #
    # MOM_data_to_plot = get_data_to_plot("splits", MOM_data_files)
    # MOM_values = [value["data"] for value in MOM_data_to_plot.values()]
    # MOM_std = [value["std"] for value in MOM_data_to_plot.values()]
    #
    # p3 = ax.bar(ind + 2*width-0.13, MOM_values, width, yerr=MOM_std, bottom = -0.5)
    #
    # # ax.set_title('Scores by group and gender')
    # ax.set_xticks(ind + width / 3)
    # ax.set_xticklabels(('simple', 'easy', 'intermediate', 'expert'))
    #
    # ax.legend((p1[0], p2[0], p3[0]), ('DP', 'JW', "MOM"))
    # ax.autoscale_view()
    #
    # # ax.set_xlim([1, len(DP_values)])
    #
    # plt.show()




def get_data_to_plot(what_goes_on_y_axis, data_files):

    data = refactor_data(data_files)

    data_to_plot = {}

    for level in data:
        data_to_plot[level] = {}
        data_to_plot[level]["data"] = data[level][what_goes_on_y_axis]["av"]
        # data_to_plot[level]["std"] = data[level][what_goes_on_y_axis]["std"]
        data_to_plot[level]["std"] = data[level][what_goes_on_y_axis]["std_replicates"]

    return data_to_plot


def refactor_data(data_files):
    av_data_per_sudoku = {}

    # get the data for each level
    for level, data_file_path in data_files.items():
        with open(data_file_path, 'rb') as data_file:
            data = pickle.load(data_file)

            #
            # # DEBUG
            # for sudoku in data:
            #     for replicate in sudoku:
            #         del replicate["clauses"]
            #         del replicate["pures"]
            #         del replicate["units"]
            # for sudoku in data:
            #     for replicate in sudoku:
            #         print(replicate)
            #
            # # DEBUG

            av_data_per_sudoku[level] = {}

            # average over the replicates within each distinct sudoku (sudoku nr)
            for sudoku_results in data:

                sudoku_nr = sudoku_results[0]["sudoku_nr"]

                av_data_per_sudoku[level][sudoku_nr] = {}
                # av_data_per_sudoku[level][sudoku_nr] = {"av_backtracks": 0,
                #                                         "std_backtracks": 0,
                #                                         "av_splits": 0,
                #                                         "std_splits": 0,
                #                                         "av_nodes": 0 }

                av_data_per_sudoku[level][sudoku_nr] = {"backtracks": {"av":0, "std":0},
                                                        "splits": {"av": 0, "std": 0},
                                                         "nodes": {"av": 0, "std": 0}}

                backtracks = []
                splits = []
                for replicate in sudoku_results:
                    backtracks.append(replicate["backtracks"])
                    splits.append(replicate["splits"])


                av_data_per_sudoku[level][sudoku_nr]["backtracks"]["av"] = np.average(backtracks)
                av_data_per_sudoku[level][sudoku_nr]["backtracks"]["std"] = np.std(backtracks)

                av_data_per_sudoku[level][sudoku_nr]["splits"]["av"] = np.average(splits)
                av_data_per_sudoku[level][sudoku_nr]["splits"]["std"] = np.std(splits)


                av_data_per_sudoku[level][sudoku_nr]["nodes"]["av"] = np.average(backtracks) + np.average(splits)
                av_data_per_sudoku[level][sudoku_nr]["nodes"]["std"] = (np.std(backtracks) + np.std(splits)) / 2

    refactored_data = {}

    for level, sudokus in av_data_per_sudoku.items():

        refactored_data[level] = {}
        refactored_data[level] = {"backtracks": {"av":0, "std":0},
                                "splits": {"av": 0, "std": 0, "all": []},
                                 "nodes": {"av": 0, "std": 0}}

        backtracks = []
        splits = []


        std_backtracks = []
        std_splits = []

        for sudoku_nr, sudoku in sudokus.items():

            backtracks.append(sudoku["backtracks"]["av"])
            splits.append(sudoku["splits"]["av"])

            std_backtracks.append(sudoku["backtracks"]["std"])
            std_splits.append(sudoku["splits"]["std"])


        refactored_data[level]["backtracks"]["av"] = np.average(backtracks)
        refactored_data[level]["backtracks"]["std"] = np.std(backtracks)
        refactored_data[level]["backtracks"]["std_replicates"] = np.average(std_backtracks)

        refactored_data[level]["splits"]["av"] = np.average(splits)
        refactored_data[level]["splits"]["std"] = np.std(splits)
        refactored_data[level]["splits"]["std_replicates"] = np.average(std_backtracks)
        refactored_data[level]["splits"]["all"] = splits

        refactored_data[level]["nodes"]["av"] = np.average(backtracks) + np.average(splits)
        refactored_data[level]["nodes"]["std"] = np.std(backtracks) + np.std(splits)
        refactored_data[level]["nodes"]["std_replicates"] = (np.average(std_backtracks) + np.average(std_splits)) / 2

    return refactored_data


if __name__ == '__main__':
    main()

