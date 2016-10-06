'''
Unit tests nclddump on a modified NetCDF file

Created on 5Oct.,2016

@author: Alex Ip
'''
import unittest
import os
from nclddump import NCLDDump

SHOW_DEBUG_OUTPUT=False

TEST_NC_PATH = 'sst.ltm.1971-2000_skos.nc' # Test file in the same directory as this script
SKOS_OPTION_LIST = ['--skos', 'lang=pl', 'altLabels=True', 'narrower=True', 'broader=True']
SKOS_OPTION_DICT = {'lang': 'pl', 'altLabels': True, 'narrower': True, 'broader': True}

TEST_DIR = os.path.abspath(os.path.dirname(__file__))

TEST_ARGS = {'CDL': ['-hs', os.path.join(TEST_DIR, TEST_NC_PATH)] + SKOS_OPTION_LIST,
             'XML': ['-x', os.path.join(TEST_DIR, TEST_NC_PATH)] + SKOS_OPTION_LIST}


nclddump_object = None

class TestNCLDDumpConstructor(unittest.TestCase):
    """Unit tests for NCLDDump class."""
    def test_constructor(self):
        '''
        Perform test of constructor
        '''
        print 'Testing NCLDDump constructor'
        global nclddump_object
        nclddump_object = NCLDDump(debug=SHOW_DEBUG_OUTPUT)
        assert nclddump_object, 'NCLDDump constructor failed'
    
class TestNCLDDumpFunctions(unittest.TestCase):
    """Unit tests for NCLDDump class."""
    
    def test_get_skos_args(self):
        print 'Testing get_skos_args function'
        global nclddump_object
        
        ncdump_arguments, skos_option_dict = nclddump_object.get_skos_args(TEST_ARGS['CDL'])
        assert ncdump_arguments == TEST_ARGS['CDL'][0:2], 'get_skos_args function failed to correctly extract ncdump arguments'
        assert skos_option_dict == SKOS_OPTION_DICT, 'get_skos_args function failed to correctly extract SKOS options'
    
class TestNCLDDumpSystem(unittest.TestCase):
    """Unit tests for NCLDDump class."""
    
    def test_process_ncdump(self):
        '''
        Perform two format tests using the same NCLDDump object to exercise caching code
        '''
        print 'Testing process_ncdump function'
        global nclddump_object
        
        for test_key in sorted(TEST_ARGS.keys()):
            print '\tTesting %s output' % test_key
            nclddump_result = nclddump_object.process_ncdump(TEST_ARGS[test_key]).read()
            if SHOW_DEBUG_OUTPUT:
                print '%s output:\n%s' % (test_key, nclddump_result)
            
            assert nclddump_object.error is None, 'process_ncdump failed for %s: %s' % (test_key, nclddump_object.error)
            
            if test_key == 'CDL':
                assert 'sst:skos_prefLabel_pl = "temperatura powierzchni morza" ;' in nclddump_result, 'SKOS prefLabel query failed'
                assert 'sst:skos_altLabels = "SST" ;' in nclddump_result, 'SKOS altLabels query failed' 
                assert 'sst:skos_broader = "" ;' in nclddump_result, 'SKOS broader query failed'
                assert 'sst:skos_narrower = "http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_skin_temperature, \
http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_subskin_temperature, \
http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/square_of_sea_surface_temperature" ;' in nclddump_result, 'SKOS narrower query failed'
            elif test_key == 'XML':
                assert '<attribute name="skos_prefLabel_pl" value="temperatura powierzchni morza"/>' in nclddump_result, 'SKOS prefLabel query failed'
                assert '<attribute name="skos_altLabels" value="SST"/>' in nclddump_result, 'SKOS altLabels query failed'
                assert '<attribute name="skos_broader" value=""/>' in nclddump_result, 'SKOS broader query failed'
                assert '<attribute name="skos_narrower" value="http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_skin_temperature, \
http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_subskin_temperature, \
http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/square_of_sea_surface_temperature"/>' in nclddump_result, 'SKOS narrower query failed'


# Define test suites
def test_suite():
    """Returns a test suite of all the tests in this module."""

    test_classes = [TestNCLDDumpConstructor,
                    TestNCLDDumpFunctions,
                    TestNCLDDumpSystem]

    suite_list = map(unittest.defaultTestLoader.loadTestsFromTestCase,
                     test_classes)

    suite = unittest.TestSuite(suite_list)

    return suite

# Define main function
def main():
    unittest.TextTestRunner(verbosity=2).run(test_suite())
    
if __name__ == '__main__':
    main()
    
    