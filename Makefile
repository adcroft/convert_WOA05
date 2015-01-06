# This Makefile documents the process for downloading the
# World Ocean Atlas, 2005, ascii data from
#    http://www.nodc.noaa.gov/OC5/WOA05/pr_woa05.html
# and converting into netcdf files.
# 
# Usage:
#   make

# Lists of: variables (V), time-periods (TP), file types (TP), grid resolutions (G)
V = t s # (t)emperature, (s)alinity, (pt) potential temperature
TP = 00 01 02 03 04 05 06 07 08 09 10 11 12 # (00) Annual mean, (01-12) Jan-Fec, (13-16) Seasons
FT = an
G = 1

SW = seawater-3.3.2
GSW = gsw-3.0.3

# Directory to place the original tar files
DOWNLOADED = tmp
# Directory into which to unpack the tar files
ASCII = tmp/ascii
# Directory into which to place netcdf conversions of ascii data
CONVERTED = tmp/converted
# Directory into which to place derived netcdf data
DERIVED = tmp/derived
# Directory into which to place final netcdf data
FINAL = final
# Directory to install python packages
PYTHON_PACKAGES = tmp/pkg

all: final.md5sums

# Rules to combine data into single files
final.md5sums: $(FINAL)/WOA05_ptemp_monthly.nc $(FINAL)/WOA05_salt_monthly.nc
	(cd $(DERIVED); $(CURDIR)/ncmd5.py *.nc) > $@

$(FINAL)/WOA05_ptemp_monthly.nc: derived.md5sums
	@mkdir -p $(FINAL)
	./concatenate_data.py $(DERIVED)/pt{0[1-9],1[0-2]}*.nc -o $@
$(FINAL)/WOA05_salt_monthly.nc: netcdf.md5sums
	@mkdir -p $(FINAL)
	./concatenate_data.py $(CONVERTED)/s{0[1-9],1[0-2]}*.nc -o $@

compare_t: $(FINAL)/WOA05_ptemp_monthly.nc
	./compare2netcdf.py $< ptemp /archive/gold/datasets/obs/WOA05_pottemp_salt.nc PTEMP
compare_s: $(FINAL)/WOA05_salt_monthly.nc
	./compare2netcdf.py $< salinity /archive/gold/datasets/obs/WOA05_pottemp_salt.nc SALT

# Rules to derive potential temperature data
derived.md5sums: $(PYTHON_PACKAGES)/lib/seawater $(foreach v, pt, $(foreach tp, $(TP), $(foreach ft, $(FT), $(DERIVED)/$(v)$(tp)$(ft)$(G).nc ) ) )
	(cd $(DERIVED); $(CURDIR)/ncmd5.py *.nc) > $@

$(DERIVED)/pt%.nc: $(CONVERTED)/t%.nc $(CONVERTED)/s%.nc
	@mkdir -p $(DERIVED)
	export PYTHONPATH=$(PYTHON_PACKAGES)/lib; ./temp2ptemp.py $^ $@

# Rules to create netcdf files
netcdf.md5sums: $(foreach v, $(V), $(foreach tp, $(TP), $(foreach ft, $(FT), $(CONVERTED)/$(v)$(tp)$(ft)$(G).nc ) ) )
	(cd $(CONVERTED); $(CURDIR)/ncmd5.py *.nc) > $@

netcdfmeta.md5sums: $(foreach v, $(V), $(foreach tp, $(TP), $(foreach ft, $(FT), $(CONVERTED)/$(v)$(tp)$(ft)$(G).cdl ) ) )
	(cd $(CONVERTED); md5sum *.cdl) > $@

%.cdl: %.nc
	ncdump -h $< > $@

# Rule to convert an ascii file into a netcdf file
$(CONVERTED)/%.nc: $(ASCII)/%
	@mkdir -p $(@D)
	./WOA05_to_netcdf.py $< $@

# This records the state of the unpacked ascii data
ascii.md5sums: $(foreach v, $(V), $(foreach tp, $(TP), $(foreach ft, $(FT), $(ASCII)/$(v)$(tp)$(ft)$(G) ) ) )
	(cd $(ASCII); md5sum [a-zA-Z][0-9][0-9]*) > $@

# Rules to unpack climatology tar files into ascii data
$(ASCII)/t%: $(DOWNLOADED)/t_climatology_1.tar
	@mkdir -p $(@D)
	tar vxf $< --directory=$(@D) $(@F).gz && gunzip -f $@.gz

$(ASCII)/s%: $(DOWNLOADED)/s_climatology_1.tar
	@mkdir -p $(@D)
	tar vxf $< --directory=$(@D) $(@F).gz && gunzip -f $@.gz

# Rules to download climatologies from NODC
$(DOWNLOADED)/t_climatology_1.tar:
	@mkdir -p $(@D)
	cd $(@D); wget ftp://ftp.nodc.noaa.gov/pub/WOA05/DATA/temperature/grid/$(@F)
	touch -m -t 200606200000 $@

$(DOWNLOADED)/s_climatology_1.tar:
	@mkdir -p $(@D)
	cd $(@D); wget ftp://ftp.nodc.noaa.gov/pub/WOA05/DATA/salinity/grid/$(@F)
	touch -m -t 200606200000 $@

# Rule to obtain seawater python package (EOS-80)
$(PYTHON_PACKAGES)/lib/seawater: $(PYTHON_PACKAGES)/$(SW)
	(cd $< ; python setup.py build -b ../)
$(PYTHON_PACKAGES)/seawater-%: $(PYTHON_PACKAGES)/seawater-%.tar.gz
	tar zvxf $< --directory $(@D)
$(PYTHON_PACKAGES)/seawater-%.tar.gz:
	@mkdir -p $(@D)
	cd $(@D); wget https://pypi.python.org/packages/source/s/seawater/$(@F)

# Rule to obtain Gibbs Sea Water python package (TEOS-10)
$(PYTHON_PACKAGES)/lib/gsw: $(PYTHON_PACKAGES)/$(GSW)
	(cd $< ; python setup.py build -b ../)
$(PYTHON_PACKAGES)/gsw-%: $(PYTHON_PACKAGES)/gsw-%.tar.gz
	(cd $(@D) ; tar zvxf $(<F))
$(PYTHON_PACKAGES)/gsw-%.tar.gz:
	@mkdir -p $(@D)
	cd $(@D); wget https://pypi.python.org/packages/source/g/gsw/$(@F)
