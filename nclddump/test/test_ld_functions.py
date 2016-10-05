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
    g = ld_functions.ConceptFetcher(test_skos_params, debug=True)
    print g.get_results('http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature')
