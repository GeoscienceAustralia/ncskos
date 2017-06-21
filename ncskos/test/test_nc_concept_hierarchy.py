'''
Created on 19 May, 2017

@author: Alex Ip
'''
import unittest
import os
from ncskos.nc_concept_hierarchy import NCConceptHierarchy

TEST_NC_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                            'data',
                            'sst.ltm.1999-2000_skos_sea_surface_temperature.nc'
                            )
                            

# Shared instances so we only invoke each constructor once
nc_concept_hierarchy_object = None

class TestNCConceptHierarchy(unittest.TestCase):
    '''
    NCConceptHierarchy - Class to extend ConceptHierarchy to work with multiple netCDF files
    '''
    def get_nc_concept_hierarchy_object(self):
        '''
        Test Constructor for class NCConceptHierarchy descended from class ConceptHierarchy
        '''
        global nc_concept_hierarchy_object
        if not nc_concept_hierarchy_object:
            print 'Testing NCConceptHierarchy constructor'
            nc_concept_hierarchy_object = NCConceptHierarchy(initial_concept_uri=None, 
                                                             lang=None, 
                                                             broader=True, 
                                                             narrower=True, # Get full tree for tests
                                                             verbose=True, 
                                                             refresh=False
                                                             )
        
            assert nc_concept_hierarchy_object, 'NCConceptHierarchy constructor failed'
         
    def test_get_concepts_from_netcdf(self):
        '''
        Recursive function to construct concept hierarchies and return all concepts for a given netCDF file
        '''
        global nc_concept_hierarchy_object
        print 'Testing NCConceptHierarchy.get_concepts_from_netcdf function'
        self.get_nc_concept_hierarchy_object()
        nc_concept_hierarchy_object.get_concepts_from_netcdf(TEST_NC_PATH)
    
    def test_get_all_dataset_variables(self):
        '''
        Function to return all (<netCDF_path> <variable_name>) tuples from cache
        '''
        global nc_concept_hierarchy_object
        print 'Testing NCConceptHierarchy.get_all_dataset_variables function'
        self.get_nc_concept_hierarchy_object()
        nc_concept_hierarchy_object.get_all_dataset_variables()
    
    def test_get_concept_from_dataset_variable(self):
        '''
        Function to return concept for a given (<netCDF_path> <variable_name>) tuple
        '''
        pass
    
    def test_get_dataset_variables_from_concept(self):
        '''
        Function to return (<netCDF_path> <variable_name>) tuples from cache which have the specified concept
        '''
        pass
        
    def test_get_dataset_variables_without_concept(self):
        '''
        Function to return all (<netCDF_path> <variable_name>) tuples from cache
        '''
        pass
        
    def test_print_concept_tree(self):
        '''
        Recursive helper function to print indented concept subtree with datasets
        '''
        pass
            
    def test_load(self):
        '''
        Overridden function to load contents from disk cache
        '''
        # Call inherited load function to load self.concept_registry from disk cache
        pass
            
            
    def test_dump(self):
        '''
        Overridden function to dump contents to disk cache
        '''
        # Call inherited dump function to dump self.concept_registry to disk cache
        pass


# Define test suites
def test_suite():
    """Returns a test suite of all the tests in this module."""

    test_classes = [
        TestNCConceptHierarchy
    ]

    suite_list = map(
        unittest.defaultTestLoader.loadTestsFromTestCase,
        test_classes
    )

    suite = unittest.TestSuite(suite_list)

    return suite


# Define main function
def main():
    unittest.TextTestRunner(verbosity=4).run(test_suite())

if __name__ == '__main__':
    main()