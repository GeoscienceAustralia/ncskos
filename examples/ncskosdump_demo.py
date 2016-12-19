'''
Created on 16Dec.,2016

@author: Alex Ip
'''
import sys
import os
import re
from glob import glob
import netCDF4

from ncskosdump.concept_hierarchy import ConceptHierarchy

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
        
    Command line arguments without a leading '-' or '--' are assumed to be targets, which can be either 
        individual netCDF files or directories containing netCDF files.
        
    Note that the default target is the "data" directory adjacent to directory containing this script
    '''
    def print_concept_tree(concept, dataset_var_concept_dict, level=0):
        '''Recursive helper function to print indented concept subtree with datasets'''
        print '\t' * level + concept['prefLabel']
        for dataset_variable in sorted([dataset_variable 
                                        for dataset_variable in dataset_var_concept_dict.keys() 
                                        if dataset_var_concept_dict[dataset_variable] == concept]):
            print '\t' * level + '  ' + ':'.join([str(item) for item in dataset_variable])
        for narrower_concept in concept['narrower']:
            print_concept_tree(narrower_concept, dataset_var_concept_dict, level+1)

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
    
    # Get list of altlabels to match
    altlabels = arg_value_dict.get('altlabels')
    altlabels = altlabels.split(',') if altlabels else []
    
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

    # Create ConceptHierarchy to build concept trees from URIs in targets
    concept_hierarchy = ConceptHierarchy(lang=arg_value_dict.get('lang'), 
                                         broader=True, # Always resolve broader to top concepts
                                         narrower=arg_value_dict.get('narrower'),
                                         verbose=verbose
                                         )   
     
    dataset_var_concept_dict = {}
    if verbose:
        print '\nReading %s netCDF files' % len(nc_path_list)
    for nc_path in nc_path_list:
        nc_dataset = netCDF4.Dataset(nc_path, 'r')
        
        data_variable_names = [variable_name for variable_name in nc_dataset.variables.keys() if len(nc_dataset.variables[variable_name].dimensions) > 1]
        for data_variable_name in sorted(data_variable_names):
            data_variable = nc_dataset.variables[data_variable_name]
            concept_uri = data_variable.__dict__.get('skos__concept_uri')
            if verbose:
                print '  Processing ' + os.path.basename(nc_path) + ':' + data_variable_name + ' with URI', concept_uri
            concept = concept_hierarchy.get_concept(concept_uri)
            dataset_var_concept_dict[(nc_path, data_variable_name)] = concept

    print '=' * 80 + '\nDatasets grouped by concept\n'
    for top_concept in sorted(concept_hierarchy.get_top_concepts()):
        print_concept_tree(top_concept, dataset_var_concept_dict)
        print
        
    uncategorised_list = sorted([dataset_variable
                              for dataset_variable in dataset_var_concept_dict.keys() 
                              if not dataset_var_concept_dict[dataset_variable]])
    if uncategorised_list:
        print 'Uncategorised (Missing URI)'
        for dataset_variable in uncategorised_list:
            print '  ' + ':'.join([str(item) for item in dataset_variable])
            
    print '\n' + '=' * 80

    # Find and print concepts and datasets matching specified altLabels
    if altlabels:
        print 'altLabel matches'
    for altlabel in altlabels:
        altlabel_concepts = concept_hierarchy.get_concept_by_altlabel(altlabel)
        if altlabel_concepts:
            print '\nConcepts and datasets with altLabel "%s":' % altlabel
            for altlabel_concept in altlabel_concepts:
                print '  %s' % altlabel_concept['prefLabel']
                for dataset_variable in sorted([dataset_variable 
                                                for dataset_variable in dataset_var_concept_dict.keys() 
                                                if dataset_var_concept_dict[dataset_variable] == altlabel_concept]):
                    print '\t' + ':'.join([str(item) for item in dataset_variable])
                    
                narrower_concepts = concept_hierarchy.get_related_concepts(altlabel_concept)
                if narrower_concepts:
                    print '  Narrower Concepts:'
                    for narrower_concept in narrower_concepts:
                        print '    %s' % narrower_concept['prefLabel']
                        for dataset_variable in sorted([dataset_variable 
                                                        for dataset_variable in dataset_var_concept_dict.keys() 
                                                        if dataset_var_concept_dict[dataset_variable] == narrower_concept]):
                            print '\t' + ':'.join([str(item) for item in dataset_variable])
        else:
            print '\nNo concepts found for altLabel "%s"' % altlabel
            
if __name__ == '__main__':
    main()