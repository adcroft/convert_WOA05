#!/usr/bin/env python

import numpy
import netCDF4
import argparse
import os
import sys; sys.path.append("./pkg/lib"); import seawater

def parseCommandLine():
  """
  Parse the command line and invoke operations.
  """
  parser = argparse.ArgumentParser(description=
      '''
      Reads WOA05 ascii files and writes as netcdf.
      ''',
      epilog='Written by A.Adcroft, 2014. No support offered.')
  parser.add_argument('tFile', type=str,
      metavar='TEMP_FILE',
      help='''netcdf file containing the 'temperature' variable.''')
  parser.add_argument('sFile', type=str,
      metavar='SALT_FILE',
      help='''netcdf file containing the 'salinity' variable.''')
  parser.add_argument('outFile', type=str,
      metavar='PTEMP_FILE',
      help='''netCDF file to construct containing potential temperature.''')
  cla = parser.parse_args()

  writeNetcdf(cla.tFile, cla.sFile, cla.outFile)

def writeNetcdf(tFile, sFile, outFile):
  """
  Calculates potential temperature for 3d/4d data in tFile and sFile and writes to outFile.
  """

  tf = netCDF4.Dataset(tFile, 'r')
  sf = netCDF4.Dataset(sFile, 'r')

  tShape = tf.variables['temperature'].shape
  sShape = sf.variables['salinity'].shape
  if not tShape == sShape: raise Exception('Input data has different shapes! Stopping.')

  lon = tf.variables['lon'][:] # Longitudes of data
  lat = tf.variables['lat'][:] # Latitudes of data
  depth = tf.variables['depth'][:] # Depth of data

  # Calculate potential temperature
  ptemp = numpy.zeros(tShape)
  for k in range(depth.shape[0]):
    T = tf.variables['temperature'][k]       # Read in-situ temperature (deg C)
    Sp = sf.variables['salinity'][k]         # Read practical salinity (psu)
    ptemp[k] = seawater.eos80.ptmp(Sp, T, depth[k])

  rg = netCDF4.Dataset(outFile, 'w', format='NETCDF4')

  # netCDF dimensions
  dLon = rg.createDimension('lon', lon.shape[0])
  dLat = rg.createDimension('lat', lat.shape[0])
  dDepth = rg.createDimension('depth', depth.shape[0])

  # netCDF variables
  vLon = rg.createVariable('lon','f4',('lon'))
  vLat = rg.createVariable('lat','f4',('lat'))
  vDepth = rg.createVariable('depth','f4',('depth'))
  vData = rg.createVariable('ptemp','f4',('depth','lat','lon'))

  # netCDF attributes
  rg.source = 'http://www.nodc.noaa.gov/OC5/WOA05/pr_woa05.html'
  vLon.name = 'Longitude'
  vLon.units = 'degrees east'
  vLat.name = 'Latitude'
  vLat.units = 'degrees north'
  vDepth.name = 'Depth'
  vDepth.units = 'm'
  vData.definition = 'Potential temperature'
  vData.units = 'degree Celsius'
  vData.missing_value = -99.9999
  vData.documentation = 'n/a'
  vData.notes = 'Converted using EOS80 with pressure obtained using seawater.eos80.pres(depth,lat).'

  # Write the data
  vLon[:] = lon
  vLat[:] = lat
  vDepth[:] = depth
  vData[:] = ptemp
  
  rg.close()

# Invoke parseCommandLine(), the top-level prodedure
if __name__ == '__main__': parseCommandLine()
