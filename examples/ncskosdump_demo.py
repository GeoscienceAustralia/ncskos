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
    def print_concept_tree(concept, dataset_var_concept_dict, level=0):
        '''Recursive function to print indented concept subtree'''
        print '\t' * level + concept['prefLabel']
        for dataset_var in sorted([dataset_var for dataset_var in dataset_var_concept_dict.keys() if dataset_var_concept_dict[dataset_var] == concept]):
            print '\t' * level + '  ' + ':'.join([str(item) for item in dataset_var])
        for narrower_concept in concept['narrower']:
            print_concept_tree(narrower_concept, dataset_var_concept_dict, level+1)

    concept_hierarchy = ConceptHierarchy()   
     
    if len(sys.argv) == 2:
        data_dir = sys.argv[1]
    else:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        
    nc_path_list = sorted(glob(os.path.join(data_dir, '*.nc')))
    
    dataset_var_concept_dict = {}
    for nc_path in nc_path_list:
        nc_dataset = netCDF4.Dataset(nc_path, 'r')
        
        data_variable_names = [variable_name for variable_name in nc_dataset.variables.keys() if len(nc_dataset.variables[variable_name].dimensions) > 1]
        for data_variable_name in sorted(data_variable_names):
            data_variable = nc_dataset.variables[data_variable_name]
            concept_uri = data_variable.__dict__.get('skos__concept_uri')
            concept = concept_hierarchy.get_concept(concept_uri)
            dataset_var_concept_dict[(nc_path, data_variable_name)] = concept
            #print os.path.basename(nc_path), data_variable_name, concept_uri

    for top_concept in [concept for concept in concept_hierarchy.get_top_concepts()]:
        print_concept_tree(top_concept, dataset_var_concept_dict)

if __name__ == '__main__':
    main()