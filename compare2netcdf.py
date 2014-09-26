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
  parser.add_argument('file1', type=str,
      metavar='FILE1',
      help='''A netcdf file.''')
  parser.add_argument('var1', type=str,
      metavar='VAR1',
      help='''The variable name in file1.''')
  parser.add_argument('file2', type=str,
      metavar='FILE2',
      help='''A netcdf file with similar data as in file1.''')
  parser.add_argument('var2', type=str,
      metavar='VAR2',
      help='''The variable name in file2.''')
  cla = parser.parse_args()

  compareNetcdfFiles(cla.file1, cla.var1, cla.file2, cla.var2)

def compareNetcdfFiles(file1, var1, file2, var2):
  """
  Calculates level-by-level stats on 3d variables in two files.
  """

  def stats(a, b, lbl1, lbl2):
    c = numpy.ma.array(a - b)
    thres = 10.*math.sqrt( numpy.mean( c*c ) )
    vrange = a.max() - a.min()
    thres = max( thres, vrange*1.e-6)
    outliers = numpy.extract(numpy.abs(c).filled(0.) > thres, c)
    c2 = numpy.ma.masked_greater(numpy.abs(c), thres)
    rms2 = math.sqrt( numpy.mean( c2*c2 ) )
    print 'rmsd=%12.5e '%rms2,lbl1,lbl2,
    if len(outliers): print len(outliers),'outliers:',outliers
    else: print

  f1 = netCDF4.Dataset(file1, 'r').variables
  f2 = netCDF4.Dataset(file2, 'r').variables

  if len(f1[var1].shape)<3 and f1[var1].shape==f2[var2].shape:
    stats(f1[var1][:], f2[var2][:], var1, var2)
  elif len(f1[var1].shape)==3 and len(f2[var2].shape)==3 and f1[var1].shape[-2:]==f2[var2].shape[-2:]:
    for k in range(min(f1[var1].shape[0], f2[var2].shape[0])):
      stats(f1[var1][k], f2[var2][k], var1+'[%i]'%k, var2+'[%i]'%k)
  elif len(f1[var1].shape)==4 and len(f2[var2].shape)==4 and f1[var1].shape[-2:]==f2[var2].shape[-2:]:
    for n in range(min(f1[var1].shape[0], f2[var2].shape[0])):
      for k in range(min(f1[var1].shape[1], f2[var2].shape[1])):
        stats(f1[var1][n][k], f2[var2][n][k], var1+'[%i,%i]'%(n,k), var2+'[%i,%i]'%(n,k))
  else: print 'Shapes do not match!',f1[var1].shape,'v',f2[var2].shape

# Invoke parseCommandLine(), the top-level prodedure
if __name__ == '__main__': parseCommandLine()
