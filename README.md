# ncskosdump
A simple command line tool that wraps and extends the well-known netCDF tool [ncdump](https://www.unidata.ucar.edu/software/netcdf/netcdf-4/newdocs/netcdf/ncdump.html), providing functionality to perform Linked Data tasks such as the dereferencing of URIs to collect vocabulary term labels. 

Note: This utility requires that the netCDF command line utilities be installed. These utilities are available from: http://www.unidata.ucar.edu/software/netcdf/docs/getting_and_building_netcdf.html

Once installed, the ncskosdump utility can be invoked as follows. Note that ncdump options are passed through to ncdump, while SKOS options are passed as <key>=<value> arguments after a "--skos" flag. The attribute name for SKOS concept lookups in the NetCDF file is 'skos_concept_uri'.

	ncskosdump <ncdump_options> <netCDF_filename> --skos <SKOS_options>

SKOS options implemented so far are as follows:

	lang=<lang_code> # e.g. 'en' or 'pl'
	altLabels=<True|False>
	narrower=<True|False>
	broader=<True|False>

Note that if no SKOS options are provided, then the prefLabel only will be retrieved in English. The output of this script (whether CDL or XML) retains full compatibility with all Unidata netCDF command line utilities, including [ncgen](https://www.unidata.ucar.edu/software/netcdf/netcdf-4/newdocs/netcdf/ncgen.html). 

For example:

	ncskosdump -hs ~/workspace/ncskosdump/ncskosdump/test/sst.ltm.1971-2000_skos.nc --skos lang=pl altLabels=True narrower=True broader=True

will replace the following CDL:

	sst:skos_concept_uri = "http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature" ;

with:

	sst:skos_broader = "" ;
	sst:skos_narrower = "http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_skin_temperature, http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_subskin_temperature, http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/square_of_sea_surface_temperature" ;
	sst:skos_prefLabel_pl = "temperatura powierzchni morza" ;
	sst:skos_altLabels = "SST" ;
	sst:skos_concept_uri = "http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature" ;
	
XML output (via the -x ncdump option) is also supported. For example:

	ncskosdump -x ~/workspace/ncskosdump/ncskosdump/test/sst.ltm.1971-2000_skos.nc --skos lang=pl altLabels=True narrower=True broader=True

will replace the following CDL:

	<attribute name="skos_concept_uri" value="http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature" />

with:

	<attribute name="skos_concept_uri" value="http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature"/>
	<attribute name="skos_broader" value=""/>
	<attribute name="skos_narrower" value="http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_skin_temperature, http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_subskin_temperature, http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/square_of_sea_surface_temperature"/>
	<attribute name="skos_prefLabel_pl" value="temperatura powierzchni morza"/>
	<attribute name="skos_altLabels" value="SST"/>

	
## Authors and Contact
Nicholas Car  
Geoscience Australia  
<nicholas.car@ga.gov.au>
  
Alex Ip  
Geoscience Australia  
<alex.ip@ga.gov.au>