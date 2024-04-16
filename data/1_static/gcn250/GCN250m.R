globalCN <- function (){
  #---Libraries-----------------------------------------------------------------------------------------------------
  library (raster)
  
  #---Change working directory
  setwd("your\\working\\directory")
  
  #---Change temp directory for raster package and create it if it does not exist
  tempdirectory<-"temp\\directory"
  dir.create(tempdirectory,showWarnings = F)
  rasterOptions(tmpdir=tempdirectory)
  
  #---download HYSOGs250m and ESA CCI-LC 2015 from cited depository to the working directory
  #---download the CN look up table from the associated depository

  #---Read the downloaded HYSOGs250m and ESA CCI-LC 2015
  HYSOGs250m <- raster("./HYSOGs250m.tif")
  ESA_CCILC_2015_300m <- raster("./ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7.tif")
  
  #---Crop the ESA CCI-LC 2015 to the extent of HYSOGs250m
  ESA_CCILC_2015_300m <- crop(ESA_CCILC_2015_300m, extent(HYSOGs250m))
  
  #---Resample ESA CCI-LC 2015 to the spatial resolution of HYSOGs250m 
  ESA_CCILC_2015_250m <- resample(ESA_CCILC_2015_300m, HYSOGs250m, method = "ngb")
  
  #---Read the CN lookup table
  CNtable <- read.csv("./CN_Table.csv", stringsAsFactors = F, check.names=FALSE)
  
  #---Create GCN raster with the same properties as HYSOG250m
  GCN250 <- raster(HYSOGs250m)

  #---Reclassify the land cover raster to CN values based on HYSOGs250 and lookup table
  #---Iterate through the soil groups 

  for (j in 3:10) {
   
    #---create land cover raster for soil group j
    LC_j <-  ESA_CCILC_2015_250m
    LC_j [HYSOGtile!=as.integer(colnames(CNtable)[j])] <- 0

    #substitute the land cover values of soil group j by the corresponding CN values from the lookup table 
    LC_j <- subs(x= LC_j,y=CNtable,by=1,which=colnames(CNtable)[j])

    GCN250[HYSOGs250m==as.integer(colnames(CNtable)[j])] <- LC_j[HYSOGs250m==as.integer(colnames(CNtable)[j])]
    
  }
  #write GCN250 to the working folder
  writeRaster(GCN250,"./GCN250.tif" ,format = "GTiff", overwrite=TRUE, dataType = "INT1U",options="COMPRESS=LZW")
}


