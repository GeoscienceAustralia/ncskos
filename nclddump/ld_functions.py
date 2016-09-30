'''
Created on 30 Sep 2016
@author: Nicholas Car
'''
import requests
import re
import rdflib


class ConceptFetcher(object):
    def __init__(self, skosprefs=None):
        """ConceptFetcher constructor

        """
        pass

    def valid_command_line_args(self, skos_params):
        """Ensure that we receive valid command line args

        :return: boolean
        """
        # ensure only allowed k/v pairs exist
        for k, v in skos_params.iteritems():
            if k not in SkosVars.keys:
                raise Exception('The command line argument {0!s} is not valid.', k)

        # ensure language param, if present, is legal
        if skos_params.get('lang') and skos_params.get('lang') not in SkosVars.language_codes:
            raise Exception('The requested language code is not a valid 2-letter ISO 639-1:200 code.')

        # if altLabels param is present, must be a boolean
        if skos_params.get('altLabels') and type(SkosVars.str_to_bool(skos_params.get('altLabels'))) != bool:
            raise Exception('An altLabels argument, if present, must be either "true" or "false"')

        # if broader param is present, must be a boolean
        if skos_params.get('broader') and type(SkosVars.str_to_bool(skos_params.get('broader'))) != bool:
            raise Exception('An broader argument, if present, must be either "true" or "false"')

        # if narrower param is present, must be a boolean
        if skos_params.get('narrower') and type(SkosVars.str_to_bool(skos_params.get('narrower'))) != bool:
            raise Exception('An narrower argument, if present, must be either "true" or "false"')

        # if we've made it this far, the args are valid
        return True

    def dereference_uri(self, uri):
        """Get the RDF data for the Concept via dereferencing the given URI

        :param uri: a valid URI for a SKOS Concept
        :return: RDF data
        """
        # get the RDF for this concept by dereferencing the URI
        # TODO: enable redirect following based on the status code (i.e. perhaps 303 & 302 but not 301 or whatever)
        s = requests.Session()
        s.max_redirects = 5  # TODO: review this magic number
        r = s.get(uri)
        # fail if not 20x status code
        r.raise_for_status()

        return r.content

    def valid_rdf(self):
        pass

    def valid_skos(self):
        pass


class SkosVars:
    keys = [
        'lang',
        'altLabels',
        'narrower',
        'broader'
    ]

    # ISO 639-1:2002: 2 letter language codes, e.g. en, pl, ru etc.
    # https://en.wikipedia.org/wiki/ISO_639-1
    language_codes = [
        'ab',
        'aa',
        'af',
        'ak',
        'sq',
        'am',
        'ar',
        'an',
        'hy',
        'as',
        'av',
        'ae',
        'ay',
        'az',
        'bm',
        'ba',
        'eu',
        'be',
        'bn',
        'bh',
        'bi',
        'bs',
        'br',
        'bg',
        'my',
        'ca',
        'ch',
        'ce',
        'ny',
        'zh',
        'cv',
        'kw',
        'co',
        'cr',
        'hr',
        'cs',
        'da',
        'dv',
        'nl',
        'dz',
        'en',
        'eo',
        'et',
        'ee',
        'fo',
        'fj',
        'fi',
        'fr',
        'ff',
        'gl',
        'ka',
        'de',
        'el',
        'gn',
        'gu',
        'ht',
        'ha',
        'he',
        'hz',
        'hi',
        'ho',
        'hu',
        'ia',
        'id',
        'ie',
        'ga',
        'ig',
        'ik',
        'io',
        'is',
        'it',
        'iu',
        'ja',
        'jv',
        'kl',
        'kn',
        'kr',
        'ks',
        'kk',
        'km',
        'ki',
        'rw',
        'ky',
        'kv',
        'kg',
        'ko',
        'ku',
        'kj',
        'la',
        'lb',
        'lg',
        'li',
        'ln',
        'lo',
        'lt',
        'lu',
        'lv',
        'gv',
        'mk',
        'mg',
        'ms',
        'ml',
        'mt',
        'mi',
        'mr',
        'mh',
        'mn',
        'na',
        'nv',
        'nd',
        'ne',
        'ng',
        'nb',
        'nn',
        'no',
        'ii',
        'nr',
        'oc',
        'oj',
        'cu',
        'om',
        'or',
        'os',
        'pa',
        'pi',
        'fa',
        'pl',
        'ps',
        'pt',
        'qu',
        'rm',
        'rn',
        'ro',
        'ru',
        'sa',
        'sc',
        'sd',
        'se',
        'sm',
        'sg',
        'sr',
        'gd',
        'sn',
        'si',
        'sk',
        'sl',
        'so',
        'st',
        'es',
        'su',
        'sw',
        'ss',
        'sv',
        'ta',
        'te',
        'tg',
        'th',
        'ti',
        'bo',
        'tk',
        'tl',
        'tn',
        'to',
        'tr',
        'ts',
        'tt',
        'tw',
        'ty',
        'ug',
        'uk',
        'ur',
        'uz',
        've',
        'vi',
        'vo',
        'wa',
        'cy',
        'wo',
        'fy',
        'xh',
        'yi',
        'yo',
        'za',
        'zu'
    ]

    def str_to_bool(s):
        if s == 'true':
            return True
        elif s == 'false':
            return False
        else:
            raise ValueError
