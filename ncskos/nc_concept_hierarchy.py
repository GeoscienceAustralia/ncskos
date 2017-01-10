'''
Created on 20Dec.,2016

@author: Alex Ip
'''
import os
import netCDF4
import yaml

from ncskos.concept_hierarchy import ConceptHierarchy

class NCConceptHierarchy(ConceptHierarchy):
    '''
    NCConceptHierarchy - Class to extend ConceptHierarchy to work with multiple netCDF files
    '''
    def __init__(self, initial_concept_uri=None, lang=None, broader=True, narrower=False, verbose=False, refresh=False):
        '''
        Constructor for class NCConceptHierarchy descended from class ConceptHierarchy
        '''
        # Cache of concepts per variable per file
        self.dataset_variable_concept_dict = {} 
        
        # Call inherited constructor
        ConceptHierarchy.__init__(self,
                                  lang=lang, 
                                  broader=broader,
                                  narrower=narrower,
                                  verbose=verbose,
                                  refresh=refresh
                                  )   
         

    def get_concepts_from_netcdf(self, nc_path):
        '''
        Recursive function to construct concept hierarchies and return all concepts for a given netCDF file
        '''
        def set_dataset_variable_concepts(dataset_variable_concept_dict, nc_path, variable_name, concept_uris):
            '''Helper function to find and set key:value in dataset_variable_concept_dict'''
            dataset_variable_concept_dict[(nc_path, variable_name)] = [] # empty list of concepts
            for concept_uri in [concept_uri.strip() for concept_uri in concept_uris.split(',')]:
            
                if self.verbose:
                    print '  Processing ' + os.path.basename(nc_path) + ':' + variable_name + ' with URI', concept_uri
                    
                concept = self.get_concept_from_uri(concept_uri)                    
                dataset_variable_concept_dict[(nc_path, variable_name)].append(concept)
            
        nc_path = os.path.abspath(nc_path)
        
        dataset_variable_concept_dict = {}
        
        nc_dataset = netCDF4.Dataset(nc_path, 'r')
    
        if hasattr(nc_dataset, 'skos__concept_uri'):
            # Set variable name to '' for global attribute
            set_dataset_variable_concepts(dataset_variable_concept_dict, nc_path, '', nc_dataset.skos__concept_uri)

        for variable_name in sorted(nc_dataset.variables.keys()):
            variable = nc_dataset.variables[variable_name]
            if hasattr(variable, 'skos__concept_uri'):
                set_dataset_variable_concepts(dataset_variable_concept_dict, nc_path, variable_name, variable.skos__concept_uri)
                
        nc_dataset.close()
        
        # Create (<netCDF_path> <variable_name>) tuple for dataset with no concepts
        dataset_variable_concept_dict = dataset_variable_concept_dict or {(nc_path, None): []}
            
        self.dataset_variable_concept_dict.update(dataset_variable_concept_dict) # Update cache

        return dataset_variable_concept_dict
    
    def get_all_dataset_variables(self):
        '''
        Function to return all (<netCDF_path> <variable_name>) tuples from cache
        '''
        return sorted(self.dataset_variable_concept_dict.keys())
    
    def get_concept_from_dataset_variable(self, dataset_variable):
        '''
        Function to return list of concepts for a given (<netCDF_path> <variable_name>) tuple
        '''
        return self.dataset_variable_concept_dict.get(dataset_variable)
    
    def get_dataset_variables_from_concept(self, concept):
        '''
        Function to return (<netCDF_path> <variable_name>) tuples from cache which have the specified concept
        '''
        return sorted([dataset_variable for dataset_variable in self.get_all_dataset_variables() 
                       if concept in self.dataset_variable_concept_dict[dataset_variable]
                       ])
        
    def get_dataset_variables_without_concept(self):
        '''
        Function to return all (<netCDF_path> <variable_name>) tuples from cache
        '''
        return sorted([dataset_variable
                       for dataset_variable in self.dataset_variable_concept_dict.keys() 
                       if not self.dataset_variable_concept_dict[dataset_variable]
                       ])
        
    def print_concept_tree(self, concept, level=0):
        '''
        Recursive helper function to print indented concept subtree with datasets
        '''
        print '\t' * level + concept.prefLabel
        for dataset_variable in self.get_dataset_variables_from_concept(concept):
            print '\t' * level + '  ' + ':'.join([str(item) for item in dataset_variable])
        for narrower_concept in concept.narrower:
            self.print_concept_tree(narrower_concept, level+1)
            
    def load(self):
        '''
        Overridden function to load contents from disk cache
        '''
        # Call inherited load function to load self.concept_registry from disk cache
        ConceptHierarchy.load(self)
        
        try:
            cached_dataset_variable_concept_dict_path = os.path.join(self.cache_dir, 'dataset_variable_concepts.yaml')
            cached_dataset_variable_concept_dict_file = open(cached_dataset_variable_concept_dict_path, 'r')
            cached_dataset_variable_concept_dict = yaml.load(cached_dataset_variable_concept_dict_file)
            cached_dataset_variable_concept_dict_file.close()
        except:
            cached_dataset_variable_concept_dict = {}
            
        for dataset_variable, concept_uris in cached_dataset_variable_concept_dict.iteritems():
            self.dataset_variable_concept_dict[dataset_variable] = [self.concept_registry.get(concept_uri) for concept_uri in concept_uris if self.concept_registry.get(concept_uri)]
            
            
    def dump(self):
        '''
        Overridden function to dump contents to disk cache
        '''
        # Call inherited dump function to dump self.concept_registry to disk cache
        ConceptHierarchy.dump(self)
        
        cached_dataset_variable_concept_dict = {dataset_variable: [concept.uri
                                                                   for concept in concepts
                                                                   if not concept.unresolved # Don't cache unresolved concepts
                                                                   ] if concepts is not None else None
                                                for dataset_variable, concepts in self.dataset_variable_concept_dict.iteritems()
                                                }
        
        cached_dataset_variable_concept_dict_path = os.path.join(self.cache_dir, 'dataset_variable_concepts.yaml')
        cached_dataset_variable_concept_dict_file = open(cached_dataset_variable_concept_dict_path, 'w')
        yaml.dump(cached_dataset_variable_concept_dict, cached_dataset_variable_concept_dict_file)
        cached_dataset_variable_concept_dict_file.close()
