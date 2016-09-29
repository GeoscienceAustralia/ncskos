# Example: languages

To get Polish langauage-only versions of the variable names in `tos_O1_2001-2002-ld.nc`, run the following `nclddump` command:

```
$ nclddump -ch -lang pl tos_O1_2001-2002-ld.nc
```

You will see the following:

```
netcdf tos_O1_2001-2002 {
dimensions:
	lon = 180 ;
	lat = 170 ;
	time = UNLIMITED ; // (24 currently)
	bnds = 2 ;
variables:
	double lon(lon) ;
		lon:standard_name = "dlugosc geograficzna" ;
		lon:units = "degrees_east" ;
		lon:axis = "X" ;
		lon:bounds = "lon_bnds" ;
		lon:original_units = "degrees_east" ;
	double lon_bnds(lon, bnds) ;
	double lat(lat) ;
		lat:standard_name = "szerokosc" ;
		lat:units = "degrees_north" ;
		lat:axis = "Y" ;
		lat:bounds = "lat_bnds" ;
		lat:original_units = "degrees_north" ;
	double lat_bnds(lat, bnds) ;
	double time(time) ;
		time:standard_name = "czas" ;
		time:units = "days since 2001-1-1" ;
		time:axis = "T" ;
		time:calendar = "360_day" ;
		time:bounds = "time_bnds" ;
		time:original_units = "seconds since 2001-1-1" ;
	double time_bnds(time, bnds) ;
	float tos(time, lat, lon) ;
		tos:standard_name = "temperatura powierzchni morza" ;
		tos:units = "K" ;
		tos:cell_methods = "time: mean (interval: 30 minutes)" ;
		tos:_FillValue = 1.e+20f ;
		tos:missing_value = 1.e+20f ;
		tos:original_name = "sosstsst" ;
		tos:original_units = "degC" ;
		tos:history = " At   16:37:23 on 01/11/2005: CMOR altered the data in the following ways: added 2.73150E+02 to yield output units;  Cyclical dimension was output starting at a different lon;" ;

// global attributes:
		:title = "IPSL  model output prepared for IPCC Fourth Assessment SRES A2 experiment" ;
		:institution = "IPSL (Institut Pierre Simon Laplace, Paris, France)" ;
		:source = "IPSL-CM4_v1 (2003) : atmosphere : LMDZ (IPSL-CM4_IPCC, 96x71x19) ; ocean ORCA2 (ipsl_cm4_v1_8, 2x2L31); sea ice LIM (ipsl_cm4_v" ;
		:contact = "Sebastien Denvil, sebastien.denvil@ipsl.jussieu.fr" ;
		:project_id = "IPCC Fourth Assessment" ;
		:table_id = "Table O1 (13 November 2004)" ;
		:experiment_id = "SRES A2 experiment" ;
		:realization = 1 ;
		:cmor_version = 0.96f ;
		:Conventions = "CF-1.0" ;
		:history = "YYYY/MM/JJ: data generated; YYYY/MM/JJ+1 data transformed  At 16:37:23 on 01/11/2005, CMOR rewrote data to comply with CF standards and IPCC Fourth Assessment requirements" ;
		:references = "Dufresne et al, Journal of Climate, 2015, vol XX, p 136" ;
		:comment = "Test drive" ;
}
```
