"""
Unit tests for ld_functions against a test URI

Created on 5Oct.,2016

@author: Alex Ip
"""
import unittest
from pprint import pprint
from ncskos import ld_functions  # ConceptFetcher, CliValuesValidator

SHOW_DEBUG_OUTPUT = False

TEST_SKOS_PARAMS = {
    'lang': 'pl',
    'altLabels': True,
    'narrower': True,
    'broader': True,
}

INVALID_SKOS_PARAMS = {
    'name': 'Freddo Frog',
    'altLabels': 'True',
    'narrower': 'False',
    'broader': True,
}

TEST_URI = 'http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature'
INVALID_URI = 'This is not a URI'

EXPECTED_RESULT = {
    'skos__broader': 'http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/surface_temperature',
    'skos__narrower': 'http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_skin_temperature, \
http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_subskin_temperature, \
http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/square_of_sea_surface_temperature',
    'skos__prefLabel_pl': 'temperatura powierzchni morza',
    'skos__altLabels': 'SST'
}

VALID_MIMETYPES = {
    'text/turtle': 'turtle',
    'text/ntriples': 'nt',
    'text/nt': 'nt',
    'text/n3': 'nt',
    'application/rdf+xml': 'rdf',
    'application/rdf+json': 'json-ld'
}

INVALID_MIMETYPE = 'nothing'

# Shared instance so we only invoke the constructor once
concept_fetcher_object = None


class TestCliValuesValidator(unittest.TestCase):
    """Unit tests for CliValuesValidator class"""

    def test_is_a_uri(self):
        """
        Perform test of CliValuesValidator.is_a_uri
        """
        print 'Testing CliValuesValidator.is_a_uri function'
        assert ld_functions.CliValuesValidator.is_a_uri(
            TEST_URI), 'CliValuesValidator.is_a_uri() function failed'
        assert not ld_functions.CliValuesValidator.is_a_uri(INVALID_URI), \
            'Negative CliValuesValidator.is_a_uri() function failed'


class TestConceptFetcherConstructor(unittest.TestCase):
    """Unit tests for ConceptFetcher constructor - RUN THIS BEFORE ANY OTHER ConceptFetcher TESTS"""

    def test_constructor(self):
        """
        Perform test of constructor
        """
        print 'Testing ConceptFetcher constructor'
        global concept_fetcher_object
        concept_fetcher_object = ld_functions.ConceptFetcher(
            TEST_SKOS_PARAMS, debug=SHOW_DEBUG_OUTPUT)

        assert concept_fetcher_object, 'NCLDDump constructor failed'


class TestConceptFetcherLowLevel(unittest.TestCase):
    """Lowest-level unit tests for ConceptFetcher class"""

    def test_valid_command_line_args(self):
        print 'Testing valid_command_line_args function'
        global concept_fetcher_object

        assert concept_fetcher_object.valid_command_line_args(TEST_SKOS_PARAMS), \
            'Failed valid_command_line_args test with %s' % TEST_SKOS_PARAMS
        try:
            assert not concept_fetcher_object.valid_command_line_args(TEST_SKOS_PARAMS), \
                'Failed negative valid_command_line_args test with %s' % INVALID_SKOS_PARAMS
        except:
            pass

    def test_valid_skos_concept_uri(self):
        print 'Testing valid_skos_concept_uri function'
        global concept_fetcher_object

        assert concept_fetcher_object.valid_skos_concept_uri(TEST_URI), \
            'Failed valid_skos_concept_uri test with %s' % TEST_URI
        try:
            assert not concept_fetcher_object.valid_skos_concept_uri(INVALID_URI), \
                'Failed negative valid_skos_concept_uri test with %s' % INVALID_URI
        except:
            pass

    def test_dereference_uri(self):
        print 'Testing dereference_uri function'
        global concept_fetcher_object

        assert '<Response [200]>' in str(concept_fetcher_object.dereference_uri(TEST_URI)), \
            'Failed dereference_uri test with %s' % TEST_URI
        try:
            assert '<Response [200]>' not in str(concept_fetcher_object.dereference_uri(INVALID_URI)), \
                'Failed negative dereference_uri test with %s' % INVALID_URI
        except:
            pass

    def test_get_rdflib_rdf_format(self):
        print 'Testing get_rdflib_rdf_format function'
        global concept_fetcher_object

        for mimetype, rdf_format in VALID_MIMETYPES.items():
            assert concept_fetcher_object.get_rdflib_rdf_format(
                mimetype + ';charset=utf-8') == rdf_format
        try:
            assert concept_fetcher_object.get_rdflib_rdf_format(INVALID_MIMETYPE) not in VALID_MIMETYPES.values(), \
                'Failed negative get_rdflib_rdf_format test with "%s"' % INVALID_MIMETYPE
        except:
            pass

    def test_valid_skos(self):
        print 'Testing test_valid_skos function'
        global concept_fetcher_object

        concept_fetcher_object.parse_rdf(
            concept_fetcher_object.dereference_uri(TEST_URI))  # Need self.g graph object

        assert concept_fetcher_object.valid_skos(
            TEST_URI), 'Failed valid_skos test with "%s"' % TEST_URI
        try:
            concept_fetcher_object.parse_rdf(
                concept_fetcher_object.dereference_uri(INVALID_URI))  # This will prob fail
            assert not concept_fetcher_object.valid_skos(INVALID_URI), \
                'Failed negative valid_skos test with "%s"' % INVALID_URI
        except:
            pass


class TestConceptFetcherMidLevel(unittest.TestCase):
    """Mid-level unit tests for ConceptFetcher class"""

    def test_get_prefLabel(self):
        print 'Testing get_prefLabel function'
        global concept_fetcher_object

        # Test default language: RResult should look something like ('sea
        # surface temperature', 'en')
        get_prefLabel_result = concept_fetcher_object.get_prefLabel(TEST_URI)
        assert get_prefLabel_result[1] == 'en', \
            'Default prefLabel language "%s" does not match "%s"' % (
                get_prefLabel_result[1], 'en')
        assert get_prefLabel_result[0] == 'sea surface temperature', \
            'Failed default language get_prefLabel test with "%s"' % TEST_URI

        # Result should look something like ('temperatura powierzchni morza',
        # 'pl')
        get_prefLabel_result = concept_fetcher_object.get_prefLabel(
            TEST_URI, lang=TEST_SKOS_PARAMS['lang'])
        assert get_prefLabel_result[1] == TEST_SKOS_PARAMS['lang'], \
            'prefLabel language "%s" does not match "%s"' % (
                get_prefLabel_result[1], TEST_SKOS_PARAMS['lang'])
        assert get_prefLabel_result[0] == EXPECTED_RESULT['skos__prefLabel_%s' % get_prefLabel_result[1]], \
            'Failed "%s" language get_prefLabel test with "%s"' % (
                TEST_SKOS_PARAMS['lang'], TEST_URI)

    def test_get_altLabels(self):
        print 'Testing get_altLabels function'
        global concept_fetcher_object

        get_altLabels_result = [
            str(altlabel) for altlabel in concept_fetcher_object.get_altLabels(TEST_URI)]
        assert sorted(get_altLabels_result) == [
            item for item in sorted(EXPECTED_RESULT['skos__altLabels'].split(', ')) if item
        ]

    def test_get_narrower(self):
        print 'Testing get_narrower function'
        global concept_fetcher_object

        get_narrower_result = [
            str(altlabel) for altlabel in concept_fetcher_object.get_narrower(TEST_URI)]
        assert sorted(get_narrower_result) == [
            item for item in sorted(EXPECTED_RESULT['skos__narrower'].split(', ')) if item
        ]

    def test_get_broader(self):
        print 'Testing get_broader function'
        global concept_fetcher_object

        get_broader_result = [
            str(altlabel) for altlabel in concept_fetcher_object.get_broader(TEST_URI)]
        assert sorted(get_broader_result) == [
            item for item in sorted(EXPECTED_RESULT['skos__broader'].split(', ')) if item
        ]


class TestConceptFetcherSystem(unittest.TestCase):
    """Top-level unit test for ConceptFetcher class"""

    def test_get_results(self):
        print 'Testing get_results function'
        global concept_fetcher_object

        result_dict = concept_fetcher_object.get_results(TEST_URI)
        if SHOW_DEBUG_OUTPUT:
            print 'Result for %s:' % TEST_URI
            pprint(result_dict)

        assert result_dict == EXPECTED_RESULT, 'Failed get_results test with "%s"' % TEST_URI


# Define test suites
def test_suite():
    """Returns a test suite of all the tests in this module."""

    test_classes = [
        TestCliValuesValidator,
        TestConceptFetcherConstructor,
        TestConceptFetcherLowLevel,
        TestConceptFetcherMidLevel,
        TestConceptFetcherSystem
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
