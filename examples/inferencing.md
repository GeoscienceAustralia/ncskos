# Example: inference grouping
One of the purposes of SKOS vocabularies is to link terms (concepts) within them in a hierarchical manner. The example vocabulary included in this code repository contains the following concept hierarchy:

* surface_temperature
    * sea_surface_temperature
        * sea_surface_skin_temperature
        * sea_surface_subskin_temperature
        * square_of_sea_surface_temperature
        
Using the hierarchy above, a netCDF file tagged with 'sea_surface_subskin_temperature' would be understood, by *inference* reasoning, to be tagged with the *broader* concepts 'sea_surface_temperature' and 'surface_temperature'. The *broader* concepts associated with a netCDF file can be retrieved with the ncskosdump command:

	ncskosdump <ncdump_options> <netCDF_filename> --skos broader=true

Therefore, files tagged with: 'sea_surface_subskin_temperature' and 'square_of_sea_surface_temperature' could be grouped together by retrieving the *broader* concepts for each file and then noticing that both file's borader concept matched contain 'sea_surface_temperature'.