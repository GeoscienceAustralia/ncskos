'''
Created on 16Dec.,2016

@author: Alex Ip
'''
import sys
import os
import re
from glob import glob
from time import sleep

from ncskosdump.nc_concept_hierarchy import NCConceptHierarchy

def main():
    '''
    Function to read concept URIs from all data variables in netCDF files and display them in a 
    concept hierarchy. Concepts and datasets matching any specified altLabels are also displayed.
    
    Command line options are specified using leading '-' or '--'. Supported options are:
        --verbose to enable verbose output
        --lang=<lang_code> where <lang_code> is a two-character ISO 639-1:200 language code
        --narrower to recursively create complete tree of narrower concepts, not just ones resolved 
            directly from URIs
        --altLabels=<altLabel_list> where <altLabel_list> is a comma-separated list of altLabels to find
        --retries=<max_retries> where <max_retries> is the maximum number of retries to attempt for
            unresolved URIs. Default retries = 0
        --delay=<retry_delay_seconds> where <retry_delay_seconds> is the number of seconds to wait before 
            each retry. Default delay = 2s
        --refresh to discard current disk cache
        
    Command line arguments without a leading '-' or '--' are assumed to be targets, which can be either 
        individual netCDF files or directories containing netCDF files.
        
    Note that the default target is the "data" directory adjacent to directory containing this script
    '''
    # Resolve "<key>=<value>" arguments. Assume key-only arguments are unary switches
    arg_value_dict = {}
    targets = []
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg[0] == '-': # Leading ' ' indicates command line switch
                key_value = [element.strip() for element in re.sub('^-+', '', arg).split('=')]
                if len(key_value) == 1:
                    key_value = [key_value[0], True] # unary argument
                                 
                # N.B: All keys are converted to lower case for internal use
                arg_value_dict[key_value[0].lower()] = key_value[1]
                
            else: # Not a command line switch - must be a target
                targets.append(arg)
        
    # Default to project "data" directory if no target specified
    if not targets:
        targets = [os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), 'data')]
        
    verbose=arg_value_dict.get('verbose')
    refresh=arg_value_dict.get('refresh')
    
    # Get list of altlabels against which to match concepts
    altlabels = arg_value_dict.get('altlabels')
    altlabels = altlabels.split(',') if altlabels else []
    
    try:
        retries = int(arg_value_dict.get('retries'))
    except:
        retries = 0 # Default to no retry                
    
    try:
        retry_delay = int(arg_value_dict.get('delay'))
    except:
        retry_delay = 2 # Default to 2s delay before retries               
    
    if verbose:
        print 'Parameters:'
        for arg_key in arg_value_dict.keys():
            print '  %s = %s' % (arg_key, arg_value_dict[arg_key])
            
        print 'Target(s):'
        for target in targets:
            print '  %s' % target

    # Build list of netCDF files
    nc_path_list = []
    for target in targets:
        if os.path.isdir(target): # Read all netCDF files in specified directory
            nc_path_list += sorted(glob(os.path.join(target, '*.nc')))
        else:
            nc_path_list += sorted(glob(target))

    # Create NCConcept to build concept trees from URIs in target netCDF files
    nc_concept_hierarchy = NCConceptHierarchy(lang=arg_value_dict.get('lang'), 
                                              broader=True, # Always resolve broader to top concepts
                                              narrower=arg_value_dict.get('narrower'),
                                              verbose=verbose,
                                              refresh=refresh
                                              )   
     
    if verbose:
        print '\nReading %s netCDF files' % len(nc_path_list)
    for nc_path in nc_path_list:
        nc_concept_hierarchy.get_concepts_from_netcdf(nc_path)
        
    # Attempt retry unresolved URIs if retries > 0
    for retry in range(retries):
        if not len(nc_concept_hierarchy.get_unresolved_concepts()):
            break

        if verbose:
            print '\nRetrying unresolved URIs - attempt %d' % (retry + 1)
            
        if (retries - retry) >= 1:
            if verbose:
                print 'Waiting %d seconds' % retry_delay
            sleep(retry_delay)

        nc_concept_hierarchy.retry_unresolved_uris()
  
    
    print '=' * 80 + '\nDatasets grouped by concept\n'
    for top_concept in sorted(nc_concept_hierarchy.get_top_concepts()):
        nc_concept_hierarchy.print_concept_tree(top_concept)
        print
        
    uncategorised_list = nc_concept_hierarchy.get_dataset_variables_without_concept()
    if uncategorised_list:
        print 'Uncategorised (Missing URI)'
        for dataset_variable in uncategorised_list:
            print '  ' + dataset_variable[0]
            
    print '\n' + '=' * 80

    # Find and print concepts and datasets matching specified altLabels
    if altlabels:
        print 'altLabel matches'
    for altlabel in altlabels:
        altlabel_concepts = nc_concept_hierarchy.get_concept_by_altlabel(altlabel)
        if altlabel_concepts:
            print '\nConcepts and datasets with altLabel "%s":' % altlabel
            for altlabel_concept in altlabel_concepts:
                print '  %s' % altlabel_concept.prefLabel
                for dataset_variable in nc_concept_hierarchy.get_dataset_variables_from_concept(altlabel_concept):
                    print '\t' + ':'.join([str(item) for item in dataset_variable])
                    
                narrower_concepts = altlabel_concept.get_related_concepts('narrower')
                if narrower_concepts:
                    print '  Narrower Concepts:'
                    for narrower_concept in narrower_concepts:
                        print '    %s' % narrower_concept.prefLabel
                        for dataset_variable in nc_concept_hierarchy.get_dataset_variables_from_concept(narrower_concept):
                            print '\t' + ':'.join([str(item) for item in dataset_variable])
        else:
            print '\nNo concepts found with altLabel "%s"' % altlabel

    if verbose:
        print '\n' + '=' * 80
                      
if __name__ == '__main__':
    main()