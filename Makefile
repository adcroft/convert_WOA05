# This Makefile documents the process for downloading the
# World Ocean Atlas, 2005, ascii data from
#    http://www.nodc.noaa.gov/OC5/WOA05/pr_woa05.html
# and converting into netcdf files.
# 
# Usage:
#   make

# Lists of: variables (V), time-periods (TP), file types (TP), grid resolutions (G)
V = t s
TP = 00 01 02 03 04 05 06 07 08 09 10 11 12
FT = an
G = 1

SW = seawater-3.3.2
GSW = gsw-3.0.3

all: ascii.md5sums netcdf.md5sums netcdfmeta.md5sums

# Rules to create netcdf files
netcdf.md5sums: $(foreach v, $(V), $(foreach tp, $(TP), $(foreach ft, $(FT), netcdf/$(v)$(tp)$(ft)$(G).nc ) ) )
	(cd netcdf; ../ncmd5.py *.nc) > $@

netcdfmeta.md5sums: $(foreach v, $(V), $(foreach tp, $(TP), $(foreach ft, $(FT), netcdf/$(v)$(tp)$(ft)$(G).cdl ) ) )
	(cd netcdf; md5sum *.cdl) > $@

%.cdl: %.nc
	ncdump -h $< > $@

# Rule to convert an ascii file into a netcdf file
netcdf/%.nc: ascii/%
	@mkdir -p netcdf
	./WOA05_to_netcdf.py $< $@

# This records the state of the unpacked ascii data
ascii.md5sums: $(foreach v, $(V), $(foreach tp, $(TP), $(foreach ft, $(FT), ascii/$(v)$(tp)$(ft)$(G) ) ) )
	(cd ascii; md5sum *) > $@

# Rules to unpack climatology tar files into ascii data
ascii/t%: t_climatology_1.tar
	@mkdir -p ascii
	cd ascii; tar vxf ../$< $(@F).gz ; gunzip -f $(@F).gz ; touch $(@F)

ascii/s%: s_climatology_1.tar
	@mkdir -p ascii
	cd ascii; tar vxf ../$< $(@F).gz ; gunzip -f $(@F).gz ; touch $(@F)

# Rules to download climatologies from NODC
t_climatology_1.tar:
	wget ftp://ftp.nodc.noaa.gov/pub/WOA05/DATA/temperature/grid/$@
	touch -m -t 200606200000 $@

s_climatology_1.tar:
	wget ftp://ftp.nodc.noaa.gov/pub/WOA05/DATA/salinity/grid/$@
	touch -m -t 200606200000 $@

# Rule to obtain seawater python package (EOS-80)
pkg/seawater: pkg/$(SW)
	(cd $< ; python setup.py build -b ../)
pkg/seawater-%: pkg/seawater-%.tar.gz
	(cd pkg ; tar zvxf $(<F))
pkg/seawater-%.tar.gz:
	@mkdir -p pkg
	cd pkg; wget https://pypi.python.org/packages/source/s/seawater/$(@F)

# Rule to obtain Gibbs Sea Water python package (TEOS-10)
pkg/gsw: pkg/$(GSW)
	(cd $< ; python setup.py build -b ../)
pkg/gsw-%: pkg/gsw-%.tar.gz
	(cd pkg ; tar zvxf $(<F))
pkg/gsw-%.tar.gz:
	@mkdir -p pkg
	cd pkg; wget https://pypi.python.org/packages/source/g/gsw/$(@F)
