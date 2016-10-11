# ncskosdump
A simple command line tool that wraps and extends the well-known netCDF tool [ncdump](https://www.unidata.ucar.edu/software/netcdf/netcdf-4/newdocs/netcdf/ncdump.html), providing functionality to perform Linked Data tasks such as the dereferencing of URIs to collect vocabulary term labels. 

Note: This utility requires that the netCDF command line utilities be installed. These utilities are available from: http://www.unidata.ucar.edu/software/netcdf/docs/getting_and_building_netcdf.html

Once installed, the ncskosdump utility can be invoked as follows. Note that ncdump options are passed through to ncdump, while SKOS options are passed as <key>=<value> arguments after a "--skos" flag. The attribute name for SKOS concept lookups in the NetCDF file is 'skos__concept_uri'.

	ncskosdump <ncdump_options> <netCDF_filename> --skos <SKOS_options>

SKOS options implemented so far are as follows:

	lang=<lang_code> # e.g. 'en' or 'pl'
	altLabels=<true|false>
	narrower=<true|false>
	broader=<true|false>

The language code is a 2-letter [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) code.

Note that if no SKOS options are provided, then the prefLabel only will be retrieved in English. The output of this script (whether CDL or XML) retains full compatibility with all Unidata netCDF command line utilities, including [ncgen](https://www.unidata.ucar.edu/software/netcdf/netcdf-4/newdocs/netcdf/ncgen.html). 

For example:

	ncskosdump -hs ~/workspace/ncskosdump/ncskosdump/test/sst.ltm.2000_skos.nc --skos lang=pl altLabels=True narrower=True broader=True

will replace the following CDL line:

	sst:skos__concept_uri = "http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature" ;

with:

	sst:skos__concept_uri = "http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature" ;
	sst:skos__broader = "" ;
	sst:skos__narrower = "http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_skin_temperature, http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_subskin_temperature, http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/square_of_sea_surface_temperature" ;
	sst:skos__prefLabel_pl = "temperatura powierzchni morza" ;
	sst:skos__altLabels = "SST" ;
	
XML output (via the -x ncdump option) is also supported. For example:

	ncskosdump -x ~/workspace/ncskosdump/ncskosdump/test/sst.ltm.1971-2000_skos.nc --skos lang=pl altLabels=True narrower=True broader=True

will replace the following XML element:

	<attribute name="skos__concept_uri" value="http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature" />

with:

	<attribute name="skos__concept_uri" value="http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature"/>
	<attribute name="skos__broader" value=""/>
	<attribute name="skos__narrower" value="http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_skin_temperature, http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_subskin_temperature, http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/square_of_sea_surface_temperature"/>
	<attribute name="skos__prefLabel_pl" value="temperatura powierzchni morza"/>
	<attribute name="skos__altLabels" value="SST"/>

	
## Authors and Contact
Nicholas Car  
Geoscience Australia  
<nicholas.car@ga.gov.au>
  
Alex Ip  
Geoscience Australia  
<alex.ip@ga.gov.au>