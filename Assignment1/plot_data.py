import matplotlib.pyplot as plt
import pickle
import numpy as np


def main():

    DP_data_files = {"simple": "data/DP_simple.p",
                    "easy": "data/DP_easy.p",
                    "intermediate": "data/DP2_intermediate.p",
                    "expert": "data/DP2_expert.p"}
    #
    # JW_data_files = {"simple": "data/JW_simple.p",
    #               "easy": "data/JW_easy.p",
    #               "intermediate": "data/JW_intermediate.p",
    #               "expert": "data/JW_expert.p"}
    #
    # MOM_data_files = {"simple": "data/MOM_simple.p",
    #                  "easy": "data/MOM_easy.p",
    #                  "intermediate": "data/MOM_intermediate.p",
    #                  "expert": "data/MOM_expert.p"}



    DP_data_to_plot = get_data_to_plot("splits", DP_data_files)
    names = list(DP_data_to_plot.keys())
    values = [value["data"] for value in DP_data_to_plot.values()]
    std = [value["std"] for value in DP_data_to_plot.values()]
    print(std)

    plt.plot(names, values, marker = 'o', label='DP')




    JW_data_to_plot = get_data_to_plot("av_splits", JW_data_files)
    values = [value["data"] for value in JW_data_to_plot.values()]
    std = [value["std"] for value in JW_data_to_plot.values()]
    plt.plot(names, values,  marker = 'o', label='JW')


    MOM_data_to_plot = get_data_to_plot("av_splits", MOM_data_files)
    values = [value["data"] for value in MOM_data_to_plot.values()]
    std = [value["std"] for value in MOM_data_to_plot.values()]
    plt.plot(names, values,  marker = 'o', label='MOM')

    # plt.errorbar(names, values, std, linestyle='None', marker='^')


    plt.ylabel('Average number of splits')
    plt.xlabel('Sudoku level')
    plt.legend()

    plt.show()



def get_data_to_plot(what_goes_on_y_axis, data_files):

    data = refactor_data(data_files)

    data_to_plot = {}

    for level in data:
        data_to_plot[level] = {}
        data_to_plot[level]["data"] = data[level][what_goes_on_y_axis]["av"]
        data_to_plot[level]["std"] = data[level][what_goes_on_y_axis]["std"]

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
                av_data_per_sudoku[level][sudoku_nr]["nodes"]["std"] = np.std(backtracks) + np.std(splits)

    refactored_data = {}

    for level, sudokus in av_data_per_sudoku.items():

        refactored_data[level] = {}
        refactored_data[level] = {"backtracks": {"av":0, "std":0},
                                "splits": {"av": 0, "std": 0},
                                 "nodes": {"av": 0, "std": 0}}

        backtracks = []
        splits = []
        for sudoku_nr, sudoku in sudokus.items():

            backtracks.append(sudoku["backtracks"]["av"])
            splits.append(sudoku["splits"]["av"])

        # av_splits = np.average(splits)
        # std_splits = np.std(splits)
        # av_backtracks = np.average(backtracks)
        # std_backtracks = np.std(backtracks)


        refactored_data[level]["backtracks"]["av"] = np.average(backtracks)
        refactored_data[level]["backtracks"]["std"] = np.std(backtracks)

        refactored_data[level]["splits"]["av"] = np.average(splits)
        refactored_data[level]["splits"]["std"] = np.std(splits)

        refactored_data[level]["nodes"]["av"] = np.average(backtracks) + np.average(splits)
        refactored_data[level]["nodes"]["std"] = np.std(backtracks) + np.std(splits)

    return refactored_data


if __name__ == '__main__':
    main()

