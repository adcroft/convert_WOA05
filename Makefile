# This Makefile documents the process for downloading the
# World Ocean Atlas, 2005, ascii data from
#    http://www.nodc.noaa.gov/OC5/WOA05/pr_woa05.html
# and converting into netcdf files.
# 
# Usage:
#   make

# Lists of: variables (V), time-periods (TP), file types (TP), grid resolutions (G)
# Variables: (t)emperature, (s)alinity, (pt) potential temperature
V = t s
# Time period: (00) Annual mean, (01-12) Jan-Fec, (13-16) Seasons
TP = 00 01 02 03 04 05 06 07 08 09 10 11 12
# File types: (an) Objectively analyzed climatology
FT = an
# Grid resolutions: (1) One-degree grid
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
# Directory into which to place final netcdf monthly data
FINAL_MONTHLY = .
# Directory into which to place final netcdf annual data
FINAL_ANNUAL = .
# Directory to install python packages
PYTHON_PACKAGES = tmp/pkg

all: md5sums
allsums: $(ASCII)/md5sums $(CONVERTED)/md5sums $(DERIVED)/md5sums $(FINAL_MONTHLY)/md5sums $(FINAL_ANNUAL)/md5sums

md5sums: $(FINAL_MONTHLY)/ptemp_WOA05_mon_24lvl.nc $(FINAL_MONTHLY)/salinity_WOA05_mon_24lvl.nc \
         $(FINAL_MONTHLY)/ptemp_WOA05_mon.nc $(FINAL_MONTHLY)/salinity_WOA05_mon.nc \
         $(FINAL_ANNUAL)/ptemp_WOA05_ann.nc $(FINAL_ANNUAL)/salinity_WOA05_ann.nc
	md5sum $^ > $@

# Rules to combine monthly data into single files deep-filled with annual climatology
$(FINAL_MONTHLY)/ptemp_WOA05_mon.nc: $(FINAL_MONTHLY) $(DERIVED)/md5sums
	python/concatenate_data.py -o $@ $(DERIVED)/pt{0[1-9],1[0-2]}*.nc -a $(DERIVED)/pt00*.nc
$(FINAL_MONTHLY)/salinity_WOA05_mon.nc: $(FINAL_MONTHLY) $(CONVERTED)/md5sums
	python/concatenate_data.py -o $@ $(CONVERTED)/s{0[1-9],1[0-2]}*.nc -a $(CONVERTED)/s00*.nc
# Rules to combine monthly data into single files on original 24 vertical levels
$(FINAL_MONTHLY)/ptemp_WOA05_mon_24lvl.nc: $(FINAL_MONTHLY) $(DERIVED)/md5sums
	python/concatenate_data.py -o $@ $(DERIVED)/pt{0[1-9],1[0-2]}*.nc
$(FINAL_MONTHLY)/salinity_WOA05_mon_24lvl.nc: $(FINAL_MONTHLY) $(CONVERTED)/md5sums
	python/concatenate_data.py -o $@ $(CONVERTED)/s{0[1-9],1[0-2]}*.nc

# Rules to create annual data files
$(FINAL_ANNUAL)/ptemp_WOA05_ann.nc: $(FINAL_ANNUAL) $(DERIVED)/md5sums
	cp $(DERIVED)/pt00an1.nc $@
$(FINAL_ANNUAL)/salinity_WOA05_ann.nc: $(FINAL_ANNUAL) $(CONVERTED)/md5sums
	cp $(CONVERTED)/s00an1.nc $@

$(FINAL_ANNUAL) $(FINAL_MONTHLY):
	@mkdir -p $@

compare_t: $(FINAL_MONTHLY)/ptemp_WOA05_ann.nc
	python/compare2netcdf.py $< ptemp /archive/gold/datasets/obs/WOA05_pottemp_salt.nc PTEMP
compare_s: $(FINAL_MONTHLY)/salinity_WOA05_mon.nc
	python/compare2netcdf.py $< salinity /archive/gold/datasets/obs/WOA05_pottemp_salt.nc SALT

# Rules to derive potential temperature data
$(DERIVED)/md5sums: $(PYTHON_PACKAGES)/lib/seawater $(foreach v, pt, $(foreach tp, $(TP), $(foreach ft, $(FT), $(DERIVED)/$(v)$(tp)$(ft)$(G).nc ) ) )
	(cd $(@D); md5sum *.nc) > $@

$(DERIVED)/pt%.nc: $(CONVERTED)/t%.nc $(CONVERTED)/s%.nc
	@mkdir -p $(DERIVED)
	export PYTHONPATH=$(PYTHON_PACKAGES)/lib; python/temp2ptemp.py $^ $@

# Rules to create netcdf files
$(CONVERTED)/md5sums: $(ASCII)/md5sums $(foreach v, $(V), $(foreach tp, $(TP), $(foreach ft, $(FT), $(CONVERTED)/$(v)$(tp)$(ft)$(G).nc ) ) )
	(cd $(@D); md5sum *.nc) > $@

%.cdl: %.nc
	ncdump -h $< > $@

# Rule to convert an ascii file into a netcdf file
$(CONVERTED)/%.nc: $(ASCII)/%
	@mkdir -p $(@D)
	python/WOA05_to_netcdf.py $< $@

# This records the state of the unpacked ascii data
$(ASCII)/md5sums: $(foreach v, $(V), $(foreach tp, $(TP), $(foreach ft, $(FT), $(ASCII)/$(v)$(tp)$(ft)$(G) ) ) )
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

# Rule to clean all intermediate files (not downloaded or final data)
clean:
	rm -rf $(DERIVED) $(ASCII) $(CONVERTED) $(PYTHON_PACKAGES)/lib  $(PYTHON_PACKAGES)/$(SW) 
