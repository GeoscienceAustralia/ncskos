'''
Unit tests nclddump on a modified NetCDF file

Created on 5Oct.,2016

@author: Alex Ip
'''
import unittest
from nclddump import NCLDDump

SHOW_DEBUG_OUTPUT=True

TEST_NC_PATH = 'sst.ltm.1971-2000_skos.nc' # Test file in the same directory as this script
SKOS_OPTION_LIST = ['--skos', 'lang=pl', 'altLabels=True', 'narrower=True', 'broader=True']

TEST_ARGS = {'CDL': ['-hs', TEST_NC_PATH] + SKOS_OPTION_LIST,
             'XML': ['-x', TEST_NC_PATH] + SKOS_OPTION_LIST}


class TestNCLDDump(unittest.TestCase):
    """Unit tests for NCLDDump class."""
    
    def __init__(self, *args, **kwargs):
        '''
        TestNCLDDump constructor
        Initialise self.nclddump_object to None
        '''
        unittest.TestCase.__init__(self, *args, **kwargs) # Call inherited constructor
        self.nclddump_object = None
    
    def test_constructor(self):
        '''
        Perform test of constructor
        '''
        print 'Testing NCLDDump constructor'
        self.nclddump_object = self.nclddump_object or NCLDDump(debug=SHOW_DEBUG_OUTPUT)
        assert self.nclddump_object, 'NCLDDump constructor failed'
    
    def test_process_ncdump(self):
        '''
        Perform two format tests using the same NCLDDump object to exercise caching code
        '''
        self.nclddump_object = self.nclddump_object or NCLDDump(debug=SHOW_DEBUG_OUTPUT)
        
        for test_key in sorted(TEST_ARGS.keys()):
            print 'Testing %s output' % test_key
            nclddump_result = self.nclddump_object.process_ncdump(TEST_ARGS[test_key]).read()
            if SHOW_DEBUG_OUTPUT:
                print '%s output:\n%s' % (test_key, nclddump_result)
            
            assert self.nclddump_object.error is None, 'process_ncdump failed for %s: %s' % (test_key, self.nclddump_object.error)
            
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

    test_classes = [TestNCLDDump]

    suite_list = map(unittest.defaultTestLoader.loadTestsFromTestCase,
                     test_classes)

    suite = unittest.TestSuite(suite_list)

    return suite

# Define main function
def main():
    unittest.TextTestRunner(verbosity=2).run(test_suite())
    
if __name__ == '__main__':
    main()
    
    