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
  data = readAscii(cla.inFile)

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

def writeNetcdf(outFile, data):
  """
  Writes data to a 1x1x33 grid netcdf file.
  """
  print outFile, data.shape
  print data[0]

# Invoke parseCommandLine(), the top-level prodedure
if __name__ == '__main__': parseCommandLine()
