'''
Created on 16Dec.,2016

@author: Alex Ip
'''
import sys
import os
from glob import glob
import netCDF4

from ncskosdump.concept_hierarchy import ConceptHierarchy

def main():
    '''
    Function to read concept URIs from all data variables in all netCDF files in dataset directory and
    display them in a concept hierarchy.
    Note that language can be specified using command line argument "lang=<lang_code>"
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
    arg_value = {}
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            key_value = [element.strip() for element in arg.split('=')]
            if len(key_value) == 1:
                key_value = ['dataset_dir', key_value[0]]
                             
            arg_value[key_value[0]] = key_value[1]
        
    # Default to project "data" directory
    if not arg_value.get('dataset_dir'):
        arg_value['dataset_dir'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        
    print 'Parameters:'
    for arg_key in arg_value.keys():
        print '  %s = %s' % (arg_key, arg_value[arg_key])
    
    concept_hierarchy = ConceptHierarchy(lang=arg_value.get('lang'))   
     
    nc_path_list = sorted(glob(os.path.join(arg_value['dataset_dir'], '*.nc')))

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
        
    print 'Uncategorised'
    for dataset_variable in sorted([dataset_variable
                              for dataset_variable in dataset_var_concept_dict.keys() 
                              if not dataset_var_concept_dict[dataset_variable]]):
        print '  ' + ':'.join([str(item) for item in dataset_variable])

if __name__ == '__main__':
    main()