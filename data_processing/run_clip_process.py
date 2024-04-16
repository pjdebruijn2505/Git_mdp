import numpy as np
import pandas as pd
import xarray as xr
import glob
import pathlib
import os.path
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import time
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

#Long code, keeps track of passed time for future reference
start_time = time.time()

#Prevent program from crashing outright.
try:
    cwd = pathlib.Path().resolve()
    src = cwd.parent
    data = src.parent.parent.parent.parent.parent.parent.parent.parent.parent
    data = os.path.join(data, 'Documents')

    # Load in the correct data paths for the data processing, subsequently load in data.
    # Replace paths with your own values.
    username = 'User '
    data_path = os.path.join(data, 'data_tana', 'catchments')
    shape_path = os.path.join(data, 'data_tana', 'catchments')
    results_path = os.path.join(data, 'data_tana', 'catchments', 'results')
    evaporation = os.path.join(data, 'data_tana', 'TAHMO', 'interpolated')
    print(f"Welcome! Your data should be located in {data_path}")
    data_files = glob.glob(os.path.join(data_path, '*.nc'))
    data_path_evap = os.path.join(evaporation, 'kriging_results_evap.nc')

    average_evap = 0.41639290443606647
    datasets = {}

    for file_path in data_files:
        # Extract the file identifier from the file name and extract it as key for the dataframe
        file_name = os.path.basename(file_path)
        file_identifier = file_name.split('_')[0]

        # Open the dataset and evaporation dataset as xarrays and identify them based on file key
        dataset = xr.open_dataset(file_path)
        dataset_evap = xr.open_dataset(data_path_evap)
        dataset = dataset.assign_coords(file_identifier=file_identifier)
        datasets[file_identifier] = dataset

    #Load in the remote sensing precipitation dataset.
    chirps_file = data_files[0]

    #Load in the shape files that are used to clip the data to the sub-catchments. They are merged together in a single dataframe.
    shape_file = os.path.join(shape_path, '*.gpkg')
    shape_files = glob.glob(shape_file)
    gdfs = []
    for file in shape_files:
        gdf = gpd.read_file(file)
        gdfs.append(gdf)

    merged_gdfs = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))


    #This function will clip the data netCDF files for the precipitation to the subcatchments as imported into the program
    #It will do this for each detected timestep in the netcdf file. The result is saved into a new xarray with all the required
    #data that the hydrological model needs to run.

    def clip_netCDF_to_geopackage(netCDF_file, geopackage_file):

        #open the geopackage file and assign the proper projection.
        shapefile_name = os.path.basename(geopackage_file)
        geopackage_gdf = gpd.read_file(geopackage_file)
        geopackage_gdf = geopackage_gdf.to_crs('EPSG:4326')


        # Open the NetCDF file and store the result. Use the geopackage file as a mask to crop the precipitation data on.
        # The raster will contain NaN in any location where the mask clipped the results away.

        with rasterio.open(netCDF_file) as src:
            data = src.read()
            clipped_data, transform = mask(src, geopackage_gdf.geometry, crop=True, nodata=np.nan)

            # The hydrological model takes in a timeseries, so the catchment-averaged precipitation is calculated
            # instead of loading in a spatially varying grid. Area of the catchment is also calculated.
            averaged_clipped_data = np.nanmean(clipped_data, axis=(1, 2))
            clipped_areas = geopackage_gdf.geometry.area

            #The results are saved into a new xarray and is returned as a dictionary combined with its file name as key
            clipped_dataset = xr.DataArray(
                averaged_clipped_data,
                dims=["time"],
                coords={"time": np.arange(averaged_clipped_data.shape[0])}
            ).to_dataset(name="precipitation")

            clipped_dataset.coords['area_m2'] = (('gdf'), clipped_areas)

            average_evap_da = xr.DataArray([average_evap] * clipped_dataset.dims['time'], dims=["time"],
                                           coords={"time": clipped_dataset.coords["time"]})
            clipped_dataset['average_evap'] = average_evap_da

        return {shapefile_name: clipped_dataset}


    # Function that simply calls the other function, required for the multiprocessing to work
    def process_single_file(args):
        return clip_netCDF_to_geopackage(*args)

    # Function that enables the parallel processing of data. Replace max-workers with number of high-performance cores
    # that are available. Function simply runs the netCDF processing n times in parallel.
    def process_files(netCDF_file, geopackage_files):
        with ProcessPoolExecutor(max_workers=4) as executor:
            args = [(netCDF_file, gpkg) for gpkg in geopackage_files]
            results = list(executor.map(process_single_file, args))
        return results

    # Starting function of file. Results are saved in a dictionary. The function loops through all the shape files
    # and then saves each entry of the dictionary into a NetCDF file the hydrological model can read.
    def main():

        netCDF_file = data_files[0]
        results = process_files(netCDF_file, shape_files)

        for result_dict in results:
            for key, ds in result_dict.items():
                filename = f"{key.replace('.gpkg', '')}.nc"  # Creating a filename for each dataset
                file_location = os.path.join(data_path, filename)
                ds.to_netcdf(file_location)

        return results

    # Fuction that prevents the freezing of function in Multi-processing environment.
    if __name__ == '__main__':
        multiprocessing.freeze_support()
        results = main()

# Print the error if any occures.
except Exception as e:
    print(f"An error occurred: {e}")

# Update the user on the timespan of the program.
end_time = time.time()
execution_time = end_time - start_time
print(f"Processing comlplete. Execution time: {execution_time} seconds")


