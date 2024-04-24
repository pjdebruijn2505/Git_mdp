import os.path
import warnings

def file_paths(root, TAHMO = False, WRA = False, catchments = False):

    # Place here the path to the root folder of the dataset
    root_folder = root.parent.parent
    root_path = os.path.join(root_folder, 'data_tana')
    results = []

    # If file structure follows read-me instructions, no other modifications to this file are neccesary.

    if TAHMO:
        TAHMO_folder = os.path.join(root_path, 'TAHMO')
        raw_folder = os.path.join(root_path, TAHMO_folder, 'raw_TAHMO')
        results_folder = os.path.join(TAHMO_folder, 'processed_TAHMO')
        interpolated_folder = os.path.join(TAHMO_folder, 'interpolated_TAHMO')
        results_animations = os.path.join(TAHMO_folder, 'results')

        results.append(raw_folder)
        results.append(results_folder)
        results.append(interpolated_folder)
        results.append(results_animations)

        print(f'The first entry is pointing to {results[-4]}, the second one to {results[-3]} and'
              f' the third one to {results[-2]}. Animations will be located in {results[-1]}')


    if WRA:
        WRA_folder = os.path.join(root_path, 'WRA')
        Garissa_folder = os.path.join(WRA_folder, 'Garissa_station')
        other_stations = os.path.join(WRA_folder, 'other_stations')

        results.append(Garissa_folder)
        results.append(other_stations)

        print(f'The first entry is pointing to {results[-2]}, the second one to {results[-1]} and')


    if catchments:
        tana_sub_catchments = os.path.join(root_path, 'catchments')
        tana_netCDF = os.path.join(tana_sub_catchments, 'results')

        results.append(tana_sub_catchments)
        results.append(tana_netCDF)

    if (len(results) == 0):
        warnings.warn("Warning, the resulting set of datapaths is empty. Make sure you specfiy the type of data you"
                      "are working with.")

    return results

