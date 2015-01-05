#!/usr/bin/env python

import numpy
import netCDF4
import argparse
import os

def parseCommandLine():
  """
  Parse the command line and invoke operations.
  """
  parser = argparse.ArgumentParser(description=
      '''
      Reads WOA05 ascii files and writes as netcdf.
      ''',
      epilog='Written by A.Adcroft, 2014. No support offered.')
  parser.add_argument('inFile', type=str,
      metavar='ASCII_FILE',
      help='''Ascii file obtained from ftp://ftp.nodc.noaa.gov/pub/WOA05/DATA/ .''')
  parser.add_argument('outFile', type=str,
      metavar='NETCDF_FILE',
      help='''netCDF file to construct.''')
  cla = parser.parse_args()

  data = readAscii(cla.inFile)
  writeNetcdf(cla.outFile, data, os.path.split(cla.inFile)[1][0])

def readAscii(inFile):
  """
  Reads the ascii file format and constructs a netcdf file with the same data.
  """
  N = 180*360*33 # Largest size of dataset in WOA05
  data = numpy.zeros(N)
  n = 0
  for line in open(inFile, 'r'):
    s = 0
    while s<80:
      data[n] = float(line[s:s+8])
      n += 1
      s += 8
    print '\rRead %i/%i (%.2f%%)'%(n,N,100.*n/N),'from',inFile,
  nk = n/(360*180)
  print ' ...',nk,'levels read'
  data = data.reshape((33,180,360))
  return data[:nk] # Removes unfilled levels

def writeNetcdf(outFile, data, varId):
  """
  Writes data to a 1x1x33 grid netcdf file, outFile.
  varId is a single character indicating the variable (t,s,o,n,p or i).
  """
  nk = data.shape[0]

  # Axis data
  dl = 360./data.shape[-1]
  lat = numpy.arange(-90.+0.5*dl,90.,dl)
  lon = numpy.arange(0.5*dl,360.,dl)
  depth = numpy.array([0,10,20,30,50,75,
                       100,125,150,200,250,300,400,500,600,700,800,900,
                       1000,1100,1200,1300,1400,1500,1750,2000,2500,3000,3500,
                       4000,4500,5000,5500,6000,6500,7000,7500,8000,8500,9000])
  depth = depth[:nk]

  rg = netCDF4.Dataset(outFile, 'w', format='NETCDF3_CLASSIC')

  # netCDF dimensions
  dLon = rg.createDimension('lon', lon.shape[0])
  dLat = rg.createDimension('lat', lat.shape[0])
  dDepth = rg.createDimension('depth', depth.shape[0])

  # netCDF variables
  vLon = rg.createVariable('lon','f4',('lon'))
  vLat = rg.createVariable('lat','f4',('lat'))
  vDepth = rg.createVariable('depth','f4',('depth'))
  vData = rg.createVariable({'t':'temperature',
                             's':'salinity'
                            }[varId], 'f4',('depth','lat','lon'))

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

  vData.long_name     = {'t':'Objectively Analyzed Climatology of In-situ temperature',
                         's':'Objectively Analyzed Climatology of Practical Salinity',
                         'o':'Objectively Analyzed Climatology of Disolved Oxygen'
                        }[varId]
  vData.standard_name = {'t':'sea_water_temperature',
                         's':'sea_water_salinity',
                         'o':'sea_water_disolved_oxygen'
                        }[varId]
  vData.definition    = {'t':'In-situ temperature',
                         's':'Practical salinity',
                         'o':'Dissolved oxygen'
                        }[varId]
  vData.units         = {'t':'degrees Celsius',
                         's':'psu',
                         'o':'ml/l'
                        }[varId]
  vData.missing_value = -99.9999
  vData.references    = {'t':'Locarnini, R. A., A. V. Mishonov, J. I. Antonov, T. P. Boyer, and H. E. Garcia, 2006. World Ocean Atlas 2005, Volume 1: Temperature. S. Levitus, Ed. NOAA Atlas NESDIS 61, U.S. Government Printing Office, Washington, D.C., 182 pp.',
                         's':'Antonov, J. I., R. A. Locarnini, T. P. Boyer, A. V. Mishonov, and H. E. Garcia, 2006. World Ocean Atlas 2005, Volume 2: Salinity. S. Levitus, Ed. NOAA Atlas NESDIS 62, U.S. Government Printing Office, Washington, D.C., 182 pp.',
                         'o':'Garcia, H. E., R. A. Locarnini, T. P. Boyer, and J. I. Antonov, 2006. World Ocean Atlas 2005, Volume 3: Dissolved Oxygen, Apparent Oxygen Utilization, and Oxygen Saturation. S. Levitus, Ed. NOAA Atlas NESDIS 63, U.S. Government Printing Office, Washington, D.C., 342 pp.'
                        }[varId]
  vData.documentation = {'t':'ftp://ftp.nodc.noaa.gov/pub/WOA05/DOC/woa05_temperature_final.pdf',
                         's':'ftp://ftp.nodc.noaa.gov/pub/WOA05/DOC/woa05_salinity_final.pdf',
                         'o':'ftp://ftp.nodc.noaa.gov/pub/WOA05/DOC/woa05_oxygen_final.pdf'
                        }[varId]
  vData.notes         = {'t':'This variable is assumed to be in-situ temperature and not potential temperature because the documentation does not make any explicit statements to the contrary.',
                         's':'Units are not documented but assumed to be psu.',
                         'o':''
                        }[varId]

  # Write the data
  vLon[:] = lon
  vLat[:] = lat
  vDepth[:] = depth
  vData[:] = data
  
  rg.close()

# Invoke parseCommandLine(), the top-level prodedure
if __name__ == '__main__': parseCommandLine()
