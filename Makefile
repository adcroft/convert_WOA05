
TARFILES = t_climatology_1.tar s_climatology_1.tar
V = t s
TP = 00 01 02 03 04 05 06 07 08 09 10 11 12
FT = an
G = 1

ascii.md5sums: $(foreach v, $(V), $(foreach tp, $(TP), $(foreach ft, $(FT), ascii/$(v)$(tp)$(ft)$(G) ) ) )
	(cd ascii; md5sum *) > ascii.md5sums

ascii/t%: t_climatology_1.tar
	mkdir -p ascii
	cd ascii; tar vxf ../$< $(@F).gz ; gunzip -f $(@F).gz ; touch $(@F)

ascii/s%: s_climatology_1.tar
	mkdir -p ascii
	cd ascii; tar vxf ../$< $(@F).gz ; gunzip -f $(@F).gz ; touch $(@F)

t_climatology_1.tar:
	wget ftp://ftp.nodc.noaa.gov/pub/WOA05/DATA/temperature/grid/$@
	touch -m -t 200606200000 $@
s_climatology_1.tar:
	wget ftp://ftp.nodc.noaa.gov/pub/WOA05/DATA/salinity/grid/$@
	touch -m -t 200606200000 $@
