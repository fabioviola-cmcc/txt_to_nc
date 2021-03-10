#!/usr/bin/python

# global reqs
import pdb
import sys
import numpy
import getopt
import logging
import traceback
from netCDF4 import Dataset

# closer level
def closer(l, levels):
    for level in range(len(levels)):
        if l < levels[level]:
            break
    if level == 0:
        i = levels[0]
    else:
        i = levels[level-1]
    return i


# main
if __name__ == "__main__":

    # create a logger
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(level=logging.DEBUG)
    
    # initialise filenames    
    input_filename = None
    output_filename = None

    # initialise lat, lon, mappings and depth
    latitudes = []
    longitudes = []
    levels = {}
    levels_ind = None
    depths = []
    
    # read input params
    logger.debug("[txt_to_nc] -- Reading input parameters...")
    options, remainder = getopt.getopt(sys.argv[1:], 'i:o', ['input=', 'output=', 'mapping='])
    for opt, arg in options:
        if opt in ('-o', '--output'):
            output_filename = arg
        elif opt in ('-i', '--input'):
            input_filename = arg
        elif opt in ('-m', '--mapping'):
            mapping_filename = arg
        else:
            logger.warn("[txt_to_nc] -- Unknown parameter %s" % opt)
    if not(input_filename) or not(output_filename) or not(mapping_filename):
        logger.error("[txt_to_nc] -- Mapping, input and output filenames are required!")

    # open txt mapping file
    logger.debug("[txt_to_nc] -- Reading mapping txt file...")
    mapfile = open(mapping_filename, 'r')
    for line in mapfile:
        lev, dep = line.split(" ")
        levels[int(lev)] = int(dep)
    levels_ind = list(levels)
        
    # open txt input file
    logger.debug("[txt_to_nc] -- Reading input txt file...")
    txtfile = open(input_filename, 'r')

    # read txt file
    linenum = 0
    for line in txtfile:

        linenum += 1
        if linenum % 1000 == 0:
            logger.debug("[txt_to_nc] -- Processed %s lines..." % linenum)
        
        try:
            
            # parse a line
            lat, lon, lev = line.split(",")
            
            # add lat and lon to latitudes and longitudes
            latitudes.append(float(lat))
            longitudes.append(float(lon))

            # is the level one of the available? if not, find the closest one
            lev = int(lev)
            if not(lev in levels_ind):
                lev = closer(lev, levels_ind)
            depths.append({"lat":float(lat), "lon":float(lon), "level":lev, "meters": levels[lev]})

        except ValueError:
            pass # skipping header lines
        
    # remove duplicates
    latitudes = list(dict.fromkeys(latitudes))
    longitudes = list(dict.fromkeys(longitudes))
    latitudes.sort()
    longitudes.sort()

    # create and open netcdf file
    logger.debug("[txt_to_nc] -- Creating netcdf file...")
    ncfile = Dataset(output_filename, "w", format="NETCDF4")
    
    # create netcdf dimensions
    logger.debug("[txt_to_nc] -- Creating NetCDF dimensions...")
    ncfile.createDimension("lat", None)
    ncfile.createDimension("lon", None)
    ncfile.createDimension("depth", None)

    # create netcdf variables
    logger.debug("[txt_to_nc] -- Creating NetCDF variables...")
    latVar = ncfile.createVariable("lat", "f4", ("lat",))
    lonVar = ncfile.createVariable("lon", "f4", ("lon",))
    depthVar = ncfile.createVariable("depth", "f4", ("depth",))
    depthovar = ncfile.createVariable("deptho", "f4", ("lat", "lon",))
    depthovar.units = "m"
    deptholevvar = ncfile.createVariable("deptho_lev", "f4", ("lat", "lon",))
    maskvar = ncfile.createVariable("mask", "b", ("depth", "lat", "lon",))

    # process depths
    logger.debug("[txt_to_nc] -- Processing depths...")
    depthvarContent = list(levels.values())
    depthovarContent = numpy.zeros((len(latitudes), len(longitudes), ))
    deptholevvarContent = numpy.zeros((len(latitudes), len(longitudes), ))
    maskvarContent = numpy.zeros((len(levels), len(latitudes), len(longitudes), ))
    
    for el in depths:
        lat = el["lat"]
        lon = el["lon"]
        lev = el["level"]
        met = el["meters"]
        latInd = latitudes.index(lat)
        lonInd = longitudes.index(lon)

        if lev <= levels[levels_ind[0]]:
            met = numpy.nan
            lev = numpy.nan
            maskvarContent[:, latInd, lonInd] = 1
        else:
            met = met
            lev = list(levels).index(lev)                    
        
        for i in range(len(levels_ind)):
            if i > lev:
                try:
                    maskvarContent[i-1, latInd, lonInd] = 1
                except:
                    print(traceback.print_exc())
                    pdb.set_trace()            
                    
        # for i in range(1, len(levels)):
        #     if i >= lev:
        #         maskvarContent[i-1, latInd, lonInd] = 0

        depthovarContent[latInd, lonInd] = met
        deptholevvarContent[latInd, lonInd] = lev
            
    # fill netcdf variables
    logger.debug("[txt_to_nc] -- Filling NetCDF variables...")
    latVar[:] = latitudes
    lonVar[:] = longitudes
    depthVar[:] = depthvarContent
    depthovar[:,:] = depthovarContent
    deptholevvar[:,:] = deptholevvarContent
    maskvar[:,:] = maskvarContent

    # close netcdf file
    logger.debug("[txt_to_nc] -- Closing NetCDF file...")
    ncfile.close()

    # close txt file
    logger.debug("[txt_to_nc] -- Closing txt file...")
    txtfile.close()
