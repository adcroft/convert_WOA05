#!/usr/bin/env python

import numpy
import netCDF4
import argparse

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
  readAsciiWriteNetcdf(cla.inFile, cla.outFile)

def readAsciiWriteNetcdf(inFile, outFile):
  """
  Reads the ascii file format and constructs a netcdf file with the same data.
  """
  print inFile, outFile

# Invoke parseCommandLine(), the top-level prodedure
if __name__ == '__main__': parseCommandLine()

