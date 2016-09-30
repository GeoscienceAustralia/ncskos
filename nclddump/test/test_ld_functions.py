if __name__ == '__main__':
    # a live test of all options using the demo vocab
    # you will see:
    #   a Polish prefLabel (temperatura powierzchni morza)
    #   1 altLabel (SST)
    #   3 narrower URIs
    from nclddump import ld_functions

    test_skos_params = {
        'lang': 'pl',
        'altLabels': True,
        'narrower': True,
        'broader': True,
    }
    g = ld_functions.ConceptFetcher(test_skos_params, 'http://pid.geoscience.gov.au/def/voc/netCDF-ld-example-tos/sea_surface_temperature')
    print g.get_results()
