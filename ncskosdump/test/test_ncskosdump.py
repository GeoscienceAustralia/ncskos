"""
Unit tests for ncskosdump against a modified NetCDF file

Created on 5Oct.,2016

@author: Alex Ip
"""
import unittest
import os
from ncskosdump import NcSKOSDump

SHOW_DEBUG_OUTPUT = False

# Test file in the same directory as this script
TEST_NC_PATH = 'sst.ltm.2000_skos.nc'
SKOS_OPTION_LIST = ['--skos', 'lang=pl',
                    'altLabels=True', 'narrower=True', 'broader=True']
SKOS_OPTION_DICT = {'lang': 'pl', 'altLabels': True,
                    'narrower': True, 'broader': True}

TEST_DIR = os.path.abspath(os.path.dirname(__file__))

TEST_ARGS = {'CDL': ['-hs', os.path.join(TEST_DIR, TEST_NC_PATH)] + SKOS_OPTION_LIST,
             'XML': ['-x', os.path.join(TEST_DIR, TEST_NC_PATH)] + SKOS_OPTION_LIST}

# Test different permutations of arguments
TEST_ARG_PERMUTATIONS = [
    SKOS_OPTION_LIST + ['-hs', os.path.join(TEST_DIR, TEST_NC_PATH)],
    SKOS_OPTION_LIST + [os.path.join(TEST_DIR, TEST_NC_PATH), '-hs'],
    ['-hs'] + SKOS_OPTION_LIST + [os.path.join(TEST_DIR, TEST_NC_PATH)],
    [os.path.join(TEST_DIR, TEST_NC_PATH)] + SKOS_OPTION_LIST + ['-hs'],
]

nclddump_object = None  # Shared instance so we only invoke the constructor once


class TestNCLDDumpConstructor(unittest.TestCase):
    """Unit tests for NcSKOSDump class."""

    def test_constructor(self):
        """
        Perform test of constructor - RUN THIS BEFORE ANY OTHER NcSKOSDump TESTS
        """
        print 'Testing NcSKOSDump constructor'
        global nclddump_object
        nclddump_object = NcSKOSDump(debug=SHOW_DEBUG_OUTPUT)
        assert nclddump_object, 'NcSKOSDump constructor failed'


class TestNCLDDumpFunctions(unittest.TestCase):
    """Unit tests for NcSKOSDump class."""

    def test_get_skos_args(self):
        print 'Testing get_skos_args function'
        global nclddump_object

        # Test straightforward arguments
        ncdump_arguments, skos_option_dict = nclddump_object.get_skos_args(TEST_ARGS[
                                                                           'CDL'])
        assert ncdump_arguments == TEST_ARGS['CDL'][
            0:2], 'get_skos_args function failed to correctly extract ncdump arguments'
        assert skos_option_dict == SKOS_OPTION_DICT, 'get_skos_args function failed to correctly extract SKOS options'

        # Test different permutations of arguments
        for args in TEST_ARG_PERMUTATIONS:
            ncdump_arguments, skos_option_dict = nclddump_object.get_skos_args(
                args)
            assert set(ncdump_arguments) == set(
                args) - set(SKOS_OPTION_LIST), 'get_skos_args function failed to correctly extract reordered ncdump arguments "%s"' % ' '.join(args)
            assert skos_option_dict == SKOS_OPTION_DICT, 'get_skos_args function failed to correctly extract reordered SKOS options from "%s"' % ' '.join(
                args)


class TestNCLDDumpSystem(unittest.TestCase):
    """Unit tests for NcSKOSDump class."""

    def test_process_ncdump(self):
        """
        Perform two format tests using the same NcSKOSDump object to exercise caching code
        """
        print 'Testing process_ncdump function'
        global nclddump_object

        for test_key in sorted(TEST_ARGS.keys()):
            print '\tTesting %s output' % test_key
            nclddump_result = nclddump_object.process_ncdump(
                TEST_ARGS[test_key]).read()
            if SHOW_DEBUG_OUTPUT:
                print '%s output:\n%s' % (test_key, nclddump_result)

            assert nclddump_object.error is None, 'process_ncdump failed for %s: %s' % (
                test_key, nclddump_object.error)

            if test_key == 'CDL':
                assert 'sst:skos__prefLabel_pl = "temperatura powierzchni morza" ;' in nclddump_result, 'SKOS prefLabel query failed'
                assert 'sst:skos__altLabels = "SST" ;' in nclddump_result, 'SKOS altLabels query failed'
                assert 'sst:skos__broader = "" ;' in nclddump_result, 'SKOS broader query failed'
                assert 'sst:skos__narrower = "http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_skin_temperature, \
http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_subskin_temperature, \
http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/square_of_sea_surface_temperature" ;' in nclddump_result, 'SKOS narrower query failed'
            elif test_key == 'XML':
                assert '<attribute name="skos__prefLabel_pl" value="temperatura powierzchni morza"/>' in nclddump_result, 'SKOS prefLabel query failed'
                assert '<attribute name="skos__altLabels" value="SST"/>' in nclddump_result, 'SKOS altLabels query failed'
                assert '<attribute name="skos__broader" value=""/>' in nclddump_result, 'SKOS broader query failed'
                assert '<attribute name="skos__narrower" value="http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_skin_temperature, \
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
