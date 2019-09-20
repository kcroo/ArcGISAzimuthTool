####################################################################################################################
# File name: ArcGISAzimuthTool.py
# Author: Kirsten Corrao
# Date: 9/20/2019
# Description: this is a tool for ArcGIS for Desktop to be used by my current workplace's soils crew. This tool
#   automates the frequent process of calculating the azimuths of soil monitoring transects and editing the new azimuth
#   transect shapefile. The user should create a polyline shapefile in the appropriate spatial reference and add an Id
#   field that can contain integers. Then they should run the SoilTransects script in the Soils - Linear Directional Mean
#   toolbox. That script will update the Id values; run the linear directional mean tool; output to the same file name as
#   the input shapefile plus _az (e.g. MyUnit123.shp outputs to MyUnit123_az.shp); delete unneeded fields in the attribute
#   table; convert line distances from meters to feet; and round azimuths to the nearest integer.
######################################################################################################################

import arcpy
import os

### TOOLBOX CLASS ###
# Contains the SoilTransects class, which can be executed in ArcGIS
class Toolbox(object):

    def __init__(self):
        self.label = "Soils - Linear Directional Mean"
        self.alias = "Soils - Linear Directional Mean"

        # List of tool classes associated with this toolbox (displays in toolbox in ArcMap)
        # can add more tools as needed for soils technicians
        self.tools = [SoilTransects]

### SOILTRANSECTS CLASS ###
# Params: 1 shapefile that contains line data; must have blank field named Id
# Output: a shapefile that contains the original line data with the attribute table containing 
#   - azimuths of each line, rounded to the nearest integer 
#   - distance of each line, converted from meters to feet 
# Details: sets Id field sequentially for each line in shapefile; runs Linear Directional Tool, which calculates azimuths;
#   outputs to shapefile with same name as original plus _az; deletes unneeded fields (DirMean, CirVar, AveX, AveY);
#   rounds azimuths to nearest integer; converts line distances from meters to feet; saves mxd file;
#   messages are displayed at various points in the script to let the user know what task was just completed

class SoilTransects(object):

    # constructor sets script label and description
    def __init__(self):
        self.label = "Soil Transects"
        self.description = "Runs the Linear Directional Tool on transects to calculate their azimuths."
        self.canRunInBackground = False

    # sets parameter as shapefile
    def getParameterInfo(self):
        param0 = arcpy.Parameter(
            displayName = "Input Features",
            name = "in_features",
            datatype = "DEShapefile",
            parameterType = "Required",
            direction = "Input")
 
        params = [param0]
        return params

    # licensing returns true (no licensing needed for this script)
    def isLicensed(self):
        return True

    # update parameters (not used)
    def updateParameters(self, parameters):
        return

    # update messages (not used)
    def updateMessages(self, parameters):
        return

    # run the script
    def execute(self, parameters, messages):
        # get parameters and set map document
        inFeatures = parameters[0].valueAsText
        mxd = arcpy.mapping.MapDocument("CURRENT")
        arcpy.AddMessage("Parameters and MXD set")

        # make path for output file with azimuths
        azimuthPath = inFeatures[:-4] + "_az.shp"

        # edit Id in transect shapefile (needed to run Linear Directional Mean tool)
        cursor = arcpy.UpdateCursor(inFeatures)
        i = 1

        for row in cursor:
            row.Id = i
            i += 1
            cursor.updateRow(row)

        # free data lock on shapefile
        del row
        del cursor

        arcpy.AddMessage("ID values updated")

        # run directional mean tool
        # parameters: input shapefile, output shapefile, orientation only, and case field
        arcpy.DirectionalMean_stats(inFeatures, azimuthPath, False, "Id")         
        arcpy.AddMessage("Directional Mean tool completed")

        # add layer of azimuth shapefile to map
        df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
        az_layer = arcpy.mapping.Layer(azimuthPath)
        arcpy.mapping.AddLayer(df, az_layer,"TOP")
        arcpy.AddMessage("Layer added to map")

        # delete unneeded fields in azimuth shapefile
        fields_to_delete = ("DirMean", "CirVar", "AveX", "AveY")

        for field in fields_to_delete:
            arcpy.DeleteField_management(azimuthPath, field)

        arcpy.AddMessage("Deleted unneeded fields")

        # round CompassA (azimuth) and convert AveLen (distance) from meters to feet
        cursor = arcpy.UpdateCursor(azimuthPath)

        for row in cursor:
            row.CompassA = round(row.CompassA)
            row.AveLen = row.AveLen * 3.28084
            cursor.updateRow(row)

        # free data lock on shapefile
        del row
        del cursor

        arcpy.AddMessage("Rounded azimuth and converted length from meters to feet")

        # save changes
        mxd.save()

        return