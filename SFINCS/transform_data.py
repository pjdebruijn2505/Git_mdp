from osgeo import gdal, ogr, osr

def clip_raster_with_kml(input_raster, kml_file, output_raster):
    
    # Open the input raster
    raster_ds = gdal.Open(input_raster)

    # Open the KML file
    kml_ds = ogr.Open(kml_file)
    kml_layer = kml_ds.GetLayer()

    # Create a memory layer to hold the clipping geometry
    mem_ds = ogr.GetDriverByName('Memory').CreateDataSource('')
    mem_layer = mem_ds.CreateLayer('polygon')

    # Copy features from KML to memory layer
    for feature in kml_layer:
        mem_layer.CreateFeature(feature)

    # Get the extent of the KML layer
    mem_layer_extent = mem_layer.GetExtent()

    # Define the extent and projection of the output raster
    output_extent = [mem_layer_extent[0], mem_layer_extent[1], mem_layer_extent[2], mem_layer_extent[3]]
    output_projection = osr.SpatialReference()
    output_projection.ImportFromEPSG(4326)  # WGS84

    # Perform the clipping
    gdal.Warp(output_raster, raster_ds, cutlineDSName=mem_ds, cropToCutline=True, dstNodata=0,
              outputBounds=output_extent, outputBoundsSRS=output_projection)

    # Close datasets
    raster_ds = None
    kml_ds = None
    mem_ds = None

    print("Raster clipping completed.")



def clip_vector_with_kml(input_vector, kml_file, output_vector):
    # Open the input vector
    input_ds = ogr.Open(input_vector)
    input_layer = input_ds.GetLayer()

    # Open the KML file
    kml_ds = ogr.Open(kml_file)
    kml_layer = kml_ds.GetLayer()

    # Get the first feature from the KML layer
    kml_feature = kml_layer.GetNextFeature()

    # Create a geometry from the KML feature
    kml_geometry = kml_feature.GetGeometryRef()

    # Create a new memory layer for the clipped features
    mem_driver = ogr.GetDriverByName('Memory')
    mem_ds = mem_driver.CreateDataSource('')
    mem_layer = mem_ds.CreateLayer('clipped', geom_type=ogr.wkbPolygon)

    # Add the geometry from the KML file to the memory layer
    mem_feature = ogr.Feature(mem_layer.GetLayerDefn())
    mem_feature.SetGeometry(kml_geometry)
    mem_layer.CreateFeature(mem_feature)

    # Perform the clipping
    output_ds = mem_driver.CreateDataSource(output_vector)
    output_layer = output_ds.CreateLayer('clipped', geom_type=ogr.wkbPolygon)

    # Create a spatial reference
    spatial_ref = input_layer.GetSpatialRef()

    # Clip the features using the KML geometry
    input_layer.Clip(mem_layer, output_layer)

    # Close datasets
    input_ds = None
    kml_ds = None
    mem_ds = None
    output_ds = None

    print("Vector clipping completed.")
