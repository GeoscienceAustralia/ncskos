# ncskos
*ncskos* is a collection of tools for manipulating netCDF files with Linked Data functionality.


## License
This repository is licensed under Creative Commons 4.0 International. See the [LICENSE deed](LICENSE) in this repository for details.


## Contacts
Author:  
**Nicholas Car**  
*Data Architect*  
Geoscience Australia  
<nicholas.car@ga.gov.au>   
<http://orcid.org/0000-0002-8742-7730>  

Author:  
**Alex Ip**  
Geoscience Australia  
<alex.ip@ga.gov.au>  
<http://orcid.org/0000-0001-8937-8904>   


## How to use
### ncskosdump
*ncskosdump* is a simple command line tool that wraps and extends the well-known netCDF tool [ncdump](https://www.unidata.ucar.edu/software/netcdf/netcdf-4/newdocs/netcdf/ncdump.html), providing functionality to perform Linked Data tasks such as the dereferencing of URIs to collect vocabulary term labels. 

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

	ncskosdump -hs ~/workspace/ncskosdump/data/sst.ltm.1999-2000_skos_sea_surface_temperature.nc --skos lang=pl altLabels=True narrower=True broader=True

will replace the following CDL line:

	sst:skos__concept_uri = "http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature" ;

with:

	sst:skos__concept_uri = "http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature" ;
	sst:skos__broader = "" ;
	sst:skos__narrower = "http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_skin_temperature, http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_subskin_temperature, http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/square_of_sea_surface_temperature" ;
	sst:skos__prefLabel_pl = "temperatura powierzchni morza" ;
	sst:skos__altLabels = "SST" ;
	
XML output (via the -x ncdump option) is also supported. For example:

	ncskosdump -x ~/workspace/ncskosdump/data/sst.ltm.1999-2000_skos.nc --skos lang=pl altLabels=True narrower=True broader=True

will replace the following XML element:

	<attribute name="skos__concept_uri" value="http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature" />

with:

	<attribute name="skos__concept_uri" value="http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature"/>
	<attribute name="skos__broader" value=""/>
	<attribute name="skos__narrower" value="http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_skin_temperature, http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_subskin_temperature, http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/square_of_sea_surface_temperature"/>
	<attribute name="skos__prefLabel_pl" value="temperatura powierzchni morza"/>
	<attribute name="skos__altLabels" value="SST"/>


Note that full unit tests can be run by entering the following:

	python -m ncskosdump.test

### Scenarios of use
See the [inference scenario](examples/inferencing.md) for a brief explanation of how to use this tool to group files linked to a hierarchical vocabulary.


## Catalog Location & Identification
This repo is catalogued in Geoscience Australia’s enterprise catalogue eCat. Its persistent URI identifier, which links directly to it, is <http://pid.geoscience.gov.au/dataset/ga/103620>.

It also has a DOI: [10.4225/25/59e42d381d04b](http://dx.doi.org/10.4225/25/59e42d381d04b).


## Citing this software
If you wish to cite this repo as you would a dataset, please do so like this:

Car, N.J. & Ip, A. (2017) ncskos code repository. Git software repository containing Python code. [DOI:10.4225/25/59e42d381d04b](http://dx.doi.org/10.4225/25/59e42d381d04b)