"""
Created on 19 May, 2017

@author: Alex Ip
"""
import unittest
from ncskos.concept_hierarchy import Concept, ConceptHierarchy

# Shared instances so we only invoke each constructor once
concept_object = None
concept_hierarchy_object = None

TEST_CONCEPT_URI = 'http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature'
TEST_ALTLABEL = 'SST'
TEST_PREFLABEL = 'sea surface temperature'
TEST_ALTLABELS = [TEST_ALTLABEL]

BAD_CONCEPT_URI = 'http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/dummy'
BAD_ALTLABEL = 'dummy_altLabel'
BAD_PREFLABEL = 'dummy concept'
BAD_ALTLABELS = [BAD_ALTLABEL]

class TestConcept(unittest.TestCase):
    '''
    Unit tests for Concept class
    '''
    def get_concept_object(self):
        '''
        Constructor for simple Concept class. Everything is public.
        '''
        global concept_object
        if not concept_object:
            print 'Testing Concept constructor'
            concept_object = Concept(concept_uri = BAD_CONCEPT_URI,
                                     prefLabel=BAD_PREFLABEL,
                                     altLabels=BAD_ALTLABELS, # List of altLabel strings
                                     unresolved=True
                                     )
            assert concept_object, 'Concept constructor failed'
        
    '''
    Unit tests for Concept class
    '''
    def test_update_from_skos_query(self):
        '''
        Function to update concept attributes from concept_fetcher.get_results() result dict
        '''
        global concept_object
        print 'Testing Concept.update_from_skos_query function'
        self.get_concept_object()
    
    def test_add_related_concept(self):
        '''
        Function to add new narrower or broader concept
        '''
        global concept_object
        print 'Testing Concept.add_related_concept function'
        self.get_concept_object()

    def test_get_related_concepts(self):
        '''
        Recursive function to return list of all narrower or broader concepts for concept. 
        '''
        global concept_object
        print 'Testing Concept.get_related_concepts function'
        self.get_concept_object()
    
    
    def test_get_sibling_concepts(self):
        '''
        Function to return all sibling concepts (narrower concepts of broader concepts)
        '''
        global concept_object
        print 'Testing Concept.get_sibling_concepts function'
        self.get_concept_object()
        
        
class TestConceptHierarchy(unittest.TestCase):
    """
    Class to track broader/narrower heirarchy of concepts
    """
    def get_concept_hierarchy_object(self):
        """
        Constructor for class ConceptHierarchy
        """
        global concept_hierarchy_object
        if not concept_hierarchy_object:
            print 'Testing ConceptHierarchy constructor'
            concept_hierarchy_object = ConceptHierarchy(initial_concept_uri=TEST_CONCEPT_URI, 
                                                        lang=None, 
                                                        broader=True, 
                                                        narrower=True, 
                                                        verbose=True,
                                                        refresh=True)
            
            assert concept_hierarchy_object, 'ConceptHierarchy constructor failed'
            concept_hierarchy_object.get_concept_from_uri(BAD_CONCEPT_URI)
    
        
    def test_get_concept_from_uri(self):
        """
        Recursive function to return dict containing altLabels and lists of broader and narrower concepts
        for the specified concept_uri.
        """
        global concept_hierarchy_object
        print 'Testing ConceptHierarchy.get_concept_from_uri function'
        self.get_concept_hierarchy_object()
        concept_hierarchy_object.get_concept_from_uri(TEST_CONCEPT_URI)
    
    
    def test_get_top_concepts(self):
        '''
        Function to return list of concepts without any "broader" concepts
        '''
        global concept_hierarchy_object
        print 'Testing ConceptHierarchy.get_top_concepts function'
        self.get_concept_hierarchy_object()
        assert concept_hierarchy_object.get_top_concepts(), 'No top concept(s) found'

    
    def test_get_bottom_concepts(self):
        '''
        Function to return list of concepts without any "narrower" concepts recorded. 
        Note: Narrower concepts may exist in vocab, but will only be recorded if their URI is resolved
        '''
        global concept_hierarchy_object
        print 'Testing ConceptHierarchy.get_bottom_concepts function'
        self.get_concept_hierarchy_object()
        assert concept_hierarchy_object.get_bottom_concepts(), 'No bottom concept(s) found'
    
    def test_get_concept_by_altlabel(self):
        '''
        Function to return list of concepts with matching altLabel (case insensitive match). 
        '''
        global concept_hierarchy_object
        print 'Testing ConceptHierarchy.get_concept_by_altlabel function'
        self.get_concept_hierarchy_object()
        assert concept_hierarchy_object.get_concept_by_altlabel(TEST_ALTLABEL), 'No concept found with AltLabel %s' % TEST_ALTLABEL
    
    def test_print_concept_tree(self):
        '''
        Recursive function to print indented concept subtree
        '''
        global concept_hierarchy_object
        print 'Testing ConceptHierarchy.print_concept_tree function'
        self.get_concept_hierarchy_object()
        for top_concept in concept_hierarchy_object.get_top_concepts():
            concept_hierarchy_object.print_concept_tree(top_concept)

    def test_get_unresolved_concepts(self):
        '''
        Function to return a list of all unresolved concepts
        '''
        global concept_hierarchy_object
        print 'Testing ConceptHierarchy.get_unresolved_concepts function'
        self.get_concept_hierarchy_object()
        assert len(concept_hierarchy_object.get_unresolved_concepts()) == 1, 'Single unresolved concept not found'

    def test_retry_unresolved_uris(self):
        '''
        Function to try to retry failed web queries and update all unresolved URIs
        '''
        global concept_hierarchy_object
        print 'Testing ConceptHierarchy.retry_unresolved_uris function'
        self.get_concept_hierarchy_object()
        concept_hierarchy_object.retry_unresolved_uris()
            
    def test_load(self):
        '''
        Function to load contents from disk cache
        '''
        global concept_hierarchy_object
        print 'Testing ConceptHierarchy.load function'
        self.get_concept_hierarchy_object()
        concept_hierarchy_object.load()
            
    def test_dump(self):
        '''
        Function to dump current contents to disk cache
        ''' 
        global concept_hierarchy_object
        print 'Testing ConceptHierarchy.dump function'
        self.get_concept_hierarchy_object()
        concept_hierarchy_object.dump()
            
    def test_z_destructor(self):
        '''
        Destructor for class ConceptHierarchy
        Dumps cache to disk
        '''
        global concept_hierarchy_object
        print 'Testing ConceptHierarchy destructor'
        self.get_concept_hierarchy_object()
        del concept_hierarchy_object
        concept_hierarchy_object = None
            
     
# Define test suites
def test_suite():
    """Returns a test suite of all the tests in this module."""

    test_classes = [
        TestConcept,
        TestConceptHierarchy
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
