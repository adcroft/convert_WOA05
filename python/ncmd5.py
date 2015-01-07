#!/usr/bin/env python

import netCDF4
import argparse
import hashlib

def parseCommandLine():
  """
  Parse the command line and invoke operations.
  """
  parser = argparse.ArgumentParser(description=
      '''
      Read each netcdf file and report the md5sum of the data for each variable.
      Note that the hash will depend on the whether the platform is big-endian or little-endian.
      ''',
      epilog='Written by A.Adcroft, 2014. No support offered.')
  parser.add_argument('ncFile', type=str,
      metavar='NETCDF_FILE',
      nargs='+',
      help='''netCDF file .''')
  cla = parser.parse_args()

  for ncFile in cla.ncFile:
    scanNetcdfFile(ncFile)

def scanNetcdfFile(ncFile):
  """
  Reads a netcdf file and calculates a hash for each variable.
  """

  rg = netCDF4.Dataset(ncFile, 'r')

  for v in rg.variables:
    print hashlib.md5(rg.variables[v][:]).hexdigest(), ncFile+':'+v

# Invoke parseCommandLine(), the top-level prodedure
if __name__ == '__main__': parseCommandLine()
