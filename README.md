convert_WOA05
=============

Tools for converting World Ocean Atlas, 2005, gridded data from ascii format to netcdf.

This package is an attempt to provide provenance for a netcdf
formatted version of the NODC World Ocean Atlas, 2005 (see
http://www.nodc.noaa.gov/OC5/WOA05/pr_woa05.html for the dataset).

This package does not supply the data in either original ascii or
final netcdf form but DOES record the state and means to download,
convert and checksum the data. It therefore provides a documentation
of how to obtain the WOA05 in netcdf format.

# To run
Everything is driven from a Makefile. To obtain data type
```
make
```
and wait a few minutes (performance depends on your network and platform).

To check that everything worked type
```
git status
```
which will hopefully tell you that you are no files have been modified.
This is checking that the *.md5sums files are consistent with those committed
to the repository, i.e. your netcdf files are validated.

# Package contents

File/directory | Purpose
--- | ---
README.md | This file
Makefile | The Makefile that governs the work-flow
ncmd5.py | A tool to md5sum each variable in a netcdf file
WOA05_to_netcdf.py* | A tool to read WOA05 ascii data and write it to a netcdf file
temp2ptemp.py | A tool to derive potential temperature from temperature and salinity
ascii.md5sums | The md5 sums of the unpacked ascii data
netcdf.md5sums | The md5 sums of the variable data in the netcdf files
netcdfmeta.md5sums | The md5 sums of the CDL files (meta-information of the netcdf files)

# Results

File/directory | Purpose
--- | ---
*_climatology_1.tar | climatology files downloaded from NOAA-NODC
ascii/ | Unpacked ascii data
netcdf/ | Will contain the converted data in netcdf files, as well as the CDL of meta-information
pkg/ | A location for installing python packages

# Requirements

Python 2.7 and the netCDF4, numpy python modules.
