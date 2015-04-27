#!/usr/bin/env python

import numpy
import netCDF4
import argparse
import math

def parseCommandLine():
  """
  Parse the command line and invoke operations.
  """
  parser = argparse.ArgumentParser(description=
      '''
      Compares the data in two netcdf files and reports level-by-level stats.
      ''',
      epilog='Written by A.Adcroft, 2014. No support offered.')
  parser.add_argument('inFiles', type=str,
      metavar='FILE',
      nargs='+',
      help='''A netcdf file.''')
  parser.add_argument('-o', type=str,
      metavar='OUTFILE',
      required=True,
      help='''The concatenated output file.''')
  cla = parser.parse_args()

  concatenateFiles(cla.inFiles, cla.o)

def concatenateFiles(inFiles, outFile):
  """
  Calculates level-by-level stats on 3d variables in two files.
  """

  hi = netCDF4.Dataset(inFiles[0], 'r')

  # Create new file and record dimension
  ho = netCDF4.Dataset(outFile, 'w', format='NETCDF3_CLASSIC')
  ho.createDimension('time',None)
  time = ho.createVariable('time','f4',['time'])

  # Copy dimensions
  for d in hi.dimensions:
    ho.createDimension(d, len(hi.dimensions[d])) 

  # Copy global attributes
  for a in hi.ncattrs():
    ho.__setattr__(a ,hi.__getattr__(a))

  # Create and copy variables
  for v in hi.variables:
    if len(hi.variables[v].shape)==1:
      hv = ho.createVariable(v, hi.variables[v].dtype, hi.variables[v].dimensions)
      hv[:] = hi.variables[v][:]
    else:
      hv = ho.createVariable(v, hi.variables[v].dtype, [u'time']+list(hi.variables[v].dimensions))
    # Copy variable attributes
    for a in hi.variables[v].ncattrs():
      hv.setncattr(a, hi.variables[v].__getattr__(a))

  hi.close()

  # For each file, copy data
  for n,f in zip(range(len(inFiles)),inFiles):
    hi = netCDF4.Dataset(f, 'r')
    for v in ho.variables:
      if 'time' in ho.variables[v].dimensions and len(ho.variables[v].dimensions)>1:
        print ho.variables[v].shape, hi.variables[v].shape,n
        ho.variables[v][n,:] = hi.variables[v][:]
    ho.variables['time'][n] = n+1
    hi.close()

  ho.close()

# Invoke parseCommandLine(), the top-level prodedure
if __name__ == '__main__': parseCommandLine()
