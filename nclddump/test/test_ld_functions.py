'''
Unit tests nclddump on a modified NetCDF file

Created on 5Oct.,2016

@author: Alex Ip
'''
import unittest
from nclddump import ld_functions

#===============================================================================
# if __name__ == '__main__':
#     # a live test of all options using the demo vocab
#     # you will see:
#     #   a Polish prefLabel (temperatura powierzchni morza)
#     #   1 altLabel (SST)
#     #   3 narrower URIs
#===============================================================================
    

SHOW_DEBUG_OUTPUT=True

TEST_SKOS_PARAMS = {'lang': 'pl',
                    'altLabels': True,
                    'narrower': True,
                    'broader': True,
                    }

INVALID_SKOS_PARAMS = {'name': 'Freddo Frog',
                    'altLabels': 'True',
                    'narrower': 'False',
                    'broader': True,
                    }
    
TEST_URI = 'http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature'
INVALID_URI = 'This is a load of crap'

VALID_MIMETYPES = {'text/turtle': 'turtle',
                   'text/ntriples': 'nt',
                   'text/nt': 'nt',
                   'text/n3': 'nt',
                   'application/rdf+xml': 'rdf',
                   'application/rdf+json': 'json-ld'
                   }
INVALID_MIMETYPE = 'crap'

class TestConceptFetcher(unittest.TestCase):
    """Unit tests for ConceptFetcher class."""
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.concept_fetcher_object = None
    
    
    def test_constructor(self):
        '''
        Perform test of constructor
        '''
        print 'Testing ConceptFetcher constructor'
        self.concept_fetcher_object = self.concept_fetcher_object or ld_functions.ConceptFetcher(TEST_SKOS_PARAMS, debug=SHOW_DEBUG_OUTPUT)
        assert self.concept_fetcher_object, 'NCLDDump constructor failed'
    
    def test_valid_command_line_args(self):
        self.concept_fetcher_object = self.concept_fetcher_object or ld_functions.ConceptFetcher(TEST_SKOS_PARAMS, debug=SHOW_DEBUG_OUTPUT)
        assert self.concept_fetcher_object.valid_command_line_args(TEST_SKOS_PARAMS), 'Failed valid_command_line_args test with %s' % TEST_SKOS_PARAMS
        try:
            assert not self.concept_fetcher_object.valid_command_line_args(TEST_SKOS_PARAMS), 'Failed negative valid_command_line_args test with %s' % INVALID_SKOS_PARAMS
        except:
            pass
        
    def test_valid_skos_concept_uri(self): 
        self.concept_fetcher_object = self.concept_fetcher_object or ld_functions.ConceptFetcher(TEST_SKOS_PARAMS, debug=SHOW_DEBUG_OUTPUT)
        assert self.concept_fetcher_object.valid_skos_concept_uri(TEST_URI), 'Failed valid_skos_concept_uri test with %s' % TEST_URI
        try:
            assert not self.concept_fetcher_object.valid_skos_concept_uri(INVALID_URI), 'Failed negative valid_skos_concept_uri test with %s' % INVALID_URI
        except:
            pass

    def test_dereference_uri(self):
        self.concept_fetcher_object = self.concept_fetcher_object or ld_functions.ConceptFetcher(TEST_SKOS_PARAMS, debug=SHOW_DEBUG_OUTPUT)
        assert '<Response [200]>' in str(self.concept_fetcher_object.dereference_uri(TEST_URI)), 'Failed dereference_uri test with %s' % TEST_URI
        try:
            assert '<Response [200]>' not in str(self.concept_fetcher_object.dereference_uri(INVALID_URI)), 'Failed negative dereference_uri test with %s' % INVALID_URI
        except:
            pass
            
    def test_get_rdflib_rdf_format(self):
        self.concept_fetcher_object = self.concept_fetcher_object or ld_functions.ConceptFetcher(TEST_SKOS_PARAMS, debug=SHOW_DEBUG_OUTPUT)
        for mimetype, rdf_format in VALID_MIMETYPES.items():
            assert self.concept_fetcher_object.get_rdflib_rdf_format(mimetype + ';charset=utf-8') == rdf_format
        try:    
            assert self.concept_fetcher_object.get_rdflib_rdf_format(INVALID_MIMETYPE) not in VALID_MIMETYPES.values(), 'Failed negative get_rdflib_rdf_format test with "%s"' % INVALID_MIMETYPE
        except:
            pass
             
            
# Define test suites
def test_suite():
    """Returns a test suite of all the tests in this module."""

    test_classes = [TestConceptFetcher]

    suite_list = map(unittest.defaultTestLoader.loadTestsFromTestCase,
                     test_classes)

    suite = unittest.TestSuite(suite_list)

    return suite

# Define main function
def main():
    unittest.TextTestRunner(verbosity=2).run(test_suite())
    
if __name__ == '__main__':
    main()
