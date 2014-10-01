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
    # Using depth in meters as pressure in dbars seems to be a common approximation
    ptemp[k] = seawater.eos80.ptmp(Sp, T, depth[k])
    # This is a test of sensitivity to the above approximation: rms differences
    # of order 1.8e-3 degC. 
    # ptemp[k] = seawater.eos80.ptmp(Sp, T, depth[k]*9.81*1035./1.e4)
    # The following is the EOS80 way and has an rms difference with the ptmp(S,T,z)
    # approximation of 1.3e-3
    # p = seawater.eos80.pres( depth[k], lat )
    # ptemp[k] = seawater.eos80.ptmp(Sp, T, (p.T + 0.*Sp.T).T)

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
  rg.source      = 'http://www.nodc.noaa.gov/OC5/WOA05/pr_woa05.html'
  rg.Conventions = 'CF-1.4'
  rg.title       = 'World Ocean Atlas 2005'
  rg.reference   = 'ftp://ftp.nodc.noaa.gov/pub/WOA05/DOC/woa05documentation.pdf'

  vLon.long_name     = 'Longitude'
  vLon.standard_name = 'longitude'
  vLon.units         = 'degrees east'
  vLon.axis          = 'X'
  vLon.description   = 'Longitude Range: 0 to 360 degrees with 0 at Greenwich Meridian and increasing towards the east.'

  vLat.long_name     = 'Latitude'
  vLat.standard_name = 'latitude'
  vLat.units         = 'degrees north'
  vLat.axis          = 'Y'
  vLat.description   = 'Latitude Range: -90 to 90 degrees with 0 at the Equator and increasing towards the north.'

  vDepth.long_name     = 'Depth'
  vDepth.standard_name = 'depth'
  vDepth.units         = 'm'
  vDepth.axis          = 'Z'
  vDepth.positive      = 'down'
  vDepth.description   = 'Standard depth levels'

  vData.long_name     = 'Objectively Analyzed Climatology of Potential temperature'
  vData.standard_name = 'sea_water_potential_temperature'
  vData.definition    = 'Potential temperature reference to 0 dbars'
  vData.units         = 'degree Celsius'
  vData.missing_value = -99.9999
 #vData.references    = 'Locarnini, R. A., A. V. Mishonov, J. I. Antonov, T. P. Boyer, and H. E. Garcia, 2006. World Ocean Atlas 2005, Volume 1: Temperature. S. Levitus, Ed. NOAA Atlas NESDIS 61, U.S. Government Printing Office, Washington, D.C., 182 pp.'
 #vData.documentation = 'ftp://ftp.nodc.noaa.gov/pub/WOA05/DOC/woa05_temperature_final.pdf'
  vData.notes         = 'Converted using EOS80 with pressure obtained using seawater.eos80.pres(depth,lat) (EOS80).'

  # Write the data
  vLon[:] = lon
  vLat[:] = lat
  vDepth[:] = depth
  vData[:] = ptemp
  
  rg.close()

# Invoke parseCommandLine(), the top-level prodedure
if __name__ == '__main__': parseCommandLine()
