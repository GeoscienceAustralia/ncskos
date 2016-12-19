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
    concept hierarchy.
    Note that language can be specified using command line argument "--lang=<lang_code>"
    Concept trees can be recursively populated down to bottom concepts if "--narrower" command line argument is used
    Targets specified on the command line can be either individual netCDF files or directories 
    containing netCDF files.
    Dataset directory defaults to project "data" directory adjacent to directory containing this script
    '''
    def print_concept_tree(concept, dataset_var_concept_dict, level=0):
        '''Recursive function to print indented concept subtree'''
        print '\t' * level + concept['prefLabel']
        for dataset_variable in sorted([dataset_variable 
                                        for dataset_variable in dataset_var_concept_dict.keys() 
                                        if dataset_var_concept_dict[dataset_variable] == concept]):
            print '\t' * level + '  ' + ':'.join([str(item) for item in dataset_variable])
        for narrower_concept in concept['narrower']:
            print_concept_tree(narrower_concept, dataset_var_concept_dict, level+1)

    # Resolve "<key>=<value>" arguments. Assume key-only argument is dataset directory
    arg_value_dict = {}
    targets = []
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg[0] == '-': # Leading ' ' indicates command line switch
                key_value = [element.strip() for element in re.sub('-+', '', arg).split('=')]
                if len(key_value) == 1:
                    key_value = [key_value[0], True] # unary argument
                                 
                arg_value_dict[key_value[0]] = key_value[1]
            else: # Not a command line switch - must be a target
                targets.append(arg)
        
    print 'Parameters:'
    for arg_key in arg_value_dict.keys():
        print '  %s = %s' % (arg_key, arg_value_dict[arg_key])
        
    # Default to project "data" directory if no target specified
    if not targets:
        targets = [os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), 'data')]
        
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
                                         broader=True,
                                         narrower=arg_value_dict.get('narrower'),
                                         verbose=arg_value_dict.get('verbose')
                                         )   
     
    dataset_var_concept_dict = {}
    print '\nReading %s netCDF files' % len(nc_path_list)
    for nc_path in nc_path_list:
        nc_dataset = netCDF4.Dataset(nc_path, 'r')
        
        data_variable_names = [variable_name for variable_name in nc_dataset.variables.keys() if len(nc_dataset.variables[variable_name].dimensions) > 1]
        for data_variable_name in sorted(data_variable_names):
            data_variable = nc_dataset.variables[data_variable_name]
            concept_uri = data_variable.__dict__.get('skos__concept_uri')
            print '  Processing ' + os.path.basename(nc_path) + ':' + data_variable_name + ' with URI', concept_uri
            concept = concept_hierarchy.get_concept(concept_uri)
            dataset_var_concept_dict[(nc_path, data_variable_name)] = concept

    print '=' * 80 + '\n'
    for top_concept in [concept for concept in concept_hierarchy.get_top_concepts()]:
        print_concept_tree(top_concept, dataset_var_concept_dict)
        print
        
    uncategorised_list = sorted([dataset_variable
                              for dataset_variable in dataset_var_concept_dict.keys() 
                              if not dataset_var_concept_dict[dataset_variable]])
    if uncategorised_list:
        print 'Uncategorised (Missing URI)'
        for dataset_variable in uncategorised_list:
            print '  ' + ':'.join([str(item) for item in dataset_variable])

if __name__ == '__main__':
    main()