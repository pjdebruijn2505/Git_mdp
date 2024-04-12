try:
    print('start imports')
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import xarray as xr
    import glob
    import platform
    import pathlib
    import os.path
    import netCDF4 as nc
    import geopandas as gpd
    import rasterio
    from rasterio.mask import mask
    from rasterio.errors import RasterioIOError
    from shapely.geometry import Point
    import time
    import json
    from scipy.spatial import cKDTree
    from concurrent.futures import ProcessPoolExecutor
    import multiprocessing
    from rasterio.crs import CRS



    print('imports complete')
    cwd = pathlib.Path().resolve()
    src = cwd.parent
    data = src.parent.parent.parent.parent.parent.parent.parent.parent.parent
    print(data)
    data = os.path.join(data, 'Documents')
    print(data)
    OS_type = platform.system()

    if OS_type == 'Darwin':
        username = 'Mats '
        data_path = os.path.join(data, 'data_tana', 'catchments')
        shape_path = os.path.join(data, 'data_tana', 'catchments')
        results_path = os.path.join(data, 'data_tana', 'catchments', 'results')
        evaporation = os.path.join(data, 'data_tana', 'TAHMO', 'interpolated')

    else:
        username = 'Mootje'
        data_path = os.path.join(data, 'OneDrive - Delft University of Technology', 'TU Delft', 'Master ENVM', 'MDP',
                                 'Model', 'Data', 'Satellite')
        shape_path = os.path.join(data, 'OneDrive - Delft University of Technology', 'TU Delft', 'Master ENVM', 'MDP',
                                  'Model', 'Data', 'Shapefiles', 'Mini_shapes')

    print(f"Welcome {username}, have a wondeful day on your {OS_type} machine. Your data should be located in {data_path}")
    print(data_path)

    data_files = glob.glob(os.path.join(data_path, '*.nc'))
    data_path_evap = os.path.join(evaporation, 'kriging_results_evap.nc')
    print(data_files)
    datasets = {}

    for file_path in data_files:
        # Extract the file identifier from the file name
        file_name = os.path.basename(file_path)  # Get just the file name
        file_identifier = file_name.split('_')[0]  # Split by underscore and take the first part
        # print(file_identifier)
        # Open the dataset
        dataset = xr.open_dataset(file_path)
        dataset_evap = xr.open_dataset(data_path_evap)
        # print(dataset)
        # Add the file identifier as a new coordinate
        dataset = dataset.assign_coords(file_identifier=file_identifier)
        # dataset_evap = dataset.assign_coords(file_identifier=file_identifier)

        # Add the dataset to the dictionary with the file identifier as the key
        datasets[file_identifier] = dataset
        # print(datasets[file_identifier])
    chirps_file = data_files[0]


    shape_file = os.path.join(shape_path, '*.gpkg')
    shape_files = glob.glob(shape_file)
    #print(shape_files)
    gdfs = []

    for file in shape_files:
        gdf = gpd.read_file(file)
        gdfs.append(gdf)

    merged_gdfs = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))


    def clip_netCDF_to_geopackage(netCDF_file, geopackage_file):
        # Obtain the name of the shapefile from the GeoPackage file
        shapefile_name = os.path.basename(geopackage_file)

        # Open the GeoPackage file
        geopackage_gdf = gpd.read_file(geopackage_file)


        #geopackage_gdf = geopackage_gdf.to_crs('EPSG:32737')
        # Open the NetCDF file
        with rasterio.open(netCDF_file) as src:
            # Read the entire timeseries data
            data = src.read()

            # Clip the NetCDF data to the GeoPackage boundaries
            clipped_data, transform = mask(src, geopackage_gdf.geometry, crop=True, nodata=np.nan)
            #clipped_data_evap, transform_evap = mask(src_evap, geopackage_gdf_evap.geometry, crop=True, nodata=np.nan)

            # Calculate the area of each clipped geometry

            clipped_areas = geopackage_gdf.geometry.area

            # Create an xarray Dataset from the clipped data
            clipped_dataset = xr.DataArray(
                clipped_data,
                dims=["time", "y", "x"],
                coords={"time": np.arange(clipped_data.shape[0]), "y": np.arange(clipped_data.shape[1]), "x": np.arange(clipped_data.shape[2])}
            ).to_dataset(name="precipitation")

                # Add the clipped areas as a new coordinate variable to the dataset
            clipped_dataset.coords['area_m2'] = (('gdf'), clipped_areas)

        return {shapefile_name: clipped_dataset}


    def process_single_file(args):
        return clip_netCDF_to_geopackage(*args)


    def process_files(netCDF_file, geopackage_files):
        with ProcessPoolExecutor(max_workers=4) as executor:
            # Create a tuple list for the arguments
            args = [(netCDF_file, gpkg) for gpkg in geopackage_files]
            results = list(executor.map(process_single_file, args))
        return results

    def main():


        # Helper function for multiprocessing to replace lambda




        # Example usage
        #data_files = ['path/to/your/netCDF.nc']  # Adjust the path as necessary
        #shape_files = shape_files  # Adjust paths as necessary
        netCDF_file = data_files[0]
        start_time = time.time()
        results = process_files(netCDF_file, shape_files)
        print(f"Processed {len(results)} files")
        end_time = time.time()
        print(f"Execution time: {end_time - start_time} seconds")


    if __name__ == '__main__':
        multiprocessing.freeze_support()  # Only needed if you plan to create a bundled executable
        main()

except Exception as e:
    print(f"An error occurred: {e}")
