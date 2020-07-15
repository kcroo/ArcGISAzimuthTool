# ArcGISAzimuthTool
This is an ArcGIS tool that I used while a soils technician for the Forest Service. It automates the frequent process of calculating the azimuths of soil monitoring transects and editing the new azimuth transect shapefile.

Before using this tool, the user should create a polyline shapefile in the appropriate spatial reference and add an Id field that can contain integers. They must also create line features that provide good coverage across the soil unit. Then they should run this script, which is called Soil Transects in the Python toolbox.

This script fills in the Id values (e.g. 1, 2, 3, etc.); runs the linear directional mean tool, which calculates the azimuths of the lines; saves the shapefile output to the same file name as the input shapefile plus _az (e.g. MyUnit123.shp outputs to MyUnit123_az.shp); deletes unneeded fields in the attribute table that were created by the linear directional mean tool; converts line distances from meters to feet; and rounds azimuths to the nearest integer.
