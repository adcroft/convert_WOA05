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
      Concatenates monthly data files into a single netcdf file.
      ''',
      epilog='Written by A.Adcroft, 2014. No support offered.')
  parser.add_argument('inFiles', type=str,
      metavar='FILE',
      nargs='+',
      help='''A netcdf file.''')
  parser.add_argument('-a', type=str,
      metavar='ANNUAL_FILE',
      default=None,
      help='''An annual climatology netcdf file to use below where monthly data is provided.''')
  parser.add_argument('-o', type=str,
      metavar='OUTFILE',
      required=True,
      help='''The concatenated output file.''')
  cla = parser.parse_args()

  concatenateFiles(cla.inFiles, cla.o, annualFile=cla.a)

def concatenateFiles(inFiles, outFile, annualFile=None):
  """
  Scans input files and writes output file
  """

  hi = netCDF4.Dataset(inFiles[0], 'r')
  if annualFile is not None: ha = netCDF4.Dataset(annualFile, 'r')

  # Create new file and record dimension
  ho = netCDF4.Dataset(outFile, 'w', format='NETCDF3_CLASSIC')
  ho.createDimension('time',None)
  time = ho.createVariable('time','f4',['time'])
  time.setncattr('long_name','month_number')
  time.setncattr('standard_name','month_number')
  time.setncattr('units','Month number')
  time.setncattr('axis','T')
  time.setncattr('description','Number of month in annual cycle, 1-12.')

  # Copy dimensions
  for d in hi.dimensions:
    if (annualFile is not None) and (d in ha.dimensions) and len(ha.dimensions[d])>len(hi.dimensions[d]):
      ho.createDimension(d, len(ha.dimensions[d])) 
    else:
      ho.createDimension(d, len(hi.dimensions[d])) 

  # Copy global attributes
  for a in hi.ncattrs():
    ho.__setattr__(a ,hi.__getattr__(a))

  # Create and copy variables
  for v in hi.variables:
    if len(hi.variables[v].shape)==1:
      if (annualFile is not None) and (v in ha.variables) and len(ha.variables[v])>len(hi.variables[v]): hptr = ha
      else: hptr = hi
      hv = ho.createVariable(v, hi.variables[v].dtype, hptr.variables[v].dimensions)
      hv[:] = hptr.variables[v][:]
    else:
      hv = ho.createVariable(v, hi.variables[v].dtype, [u'time']+list(hi.variables[v].dimensions))
    # Copy variable attributes
    for a in hi.variables[v].ncattrs():
      hv.setncattr(a, hi.variables[v].__getattr__(a))

  hi.close()

  # For each file, copy data
  nza = 0
  for n,f in zip(range(len(inFiles)),inFiles):
    hi = netCDF4.Dataset(f, 'r')
    for v in ho.variables:
      if 'time' in ho.variables[v].dimensions and len(ho.variables[v].dimensions)>1:
        nzi = hi.variables[v].shape[-3]
        if annualFile is not None: nza = ha.variables[v].shape[-3]
        print ho.variables[v].shape, hi.variables[v].shape, n, nzi, nza
        ho.variables[v][n,:nzi] = hi.variables[v][:]
        if nza>nzi: ho.variables[v][n,nzi:] = ha.variables[v][nzi:]
    ho.variables['time'][n] = n+1
    hi.close()

  ho.close()

# Invoke parseCommandLine(), the top-level prodedure
if __name__ == '__main__': parseCommandLine()
