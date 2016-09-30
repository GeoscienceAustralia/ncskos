'''
Created on 30 Sep 2016
@author: Nicholas Car
'''
import requests
import re
import rdflib
from StringIO import StringIO


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
            if k not in CliValuesValidator.keys:
                raise Exception('The command line argument {0!s} is not valid.', k)

        # ensure language param, if present, is legal
        if skos_params.get('lang') and skos_params.get('lang') not in CliValuesValidator.language_codes:
            raise Exception('The requested language code is not a valid 2-letter ISO 639-1:200 code.')

        # if altLabels param is present, must be a boolean
        if skos_params.get('altLabels') and type(skos_params.get('altLabels')) != bool:
            raise Exception('An altLabels argument, if present, must be either "true" or "false"')

        # if broader param is present, must be a boolean
        if skos_params.get('broader') and type(skos_params.get('broader')) != bool:
            raise Exception('An broader argument, if present, must be either "true" or "false"')

        # if narrower param is present, must be a boolean
        if skos_params.get('narrower') and type(skos_params.get('narrower')) != bool:
            raise Exception('An narrower argument, if present, must be either "true" or "false"')

        # if we've made it this far, the args are valid
        return True

    def valid_skos_concept_uri(self, potential_uri):
        if not CliValuesValidator.is_a_uri(potential_uri):
            raise Exception('The skos_concept_uri netCDF header value {} is not a valid URI.', potential_uri)

    def dereference_uri(self, uri):
        """Get the RDF data for the Concept via dereferencing the given URI

        :param uri: a valid URI for a SKOS Concept
        :return: RDF data
        """
        # get the RDF for this concept by dereferencing the URI
        # TODO: enable redirect following based on the status code (i.e. perhaps 303 & 302 but not 301 or whatever)
        s = requests.Session()
        s.max_redirects = 3  # TODO: review this magic number
        r = s.get(uri)
        # fail if not 20x status code
        r.raise_for_status()

        return r

    def get_rdflib_rdf_format(self, mimetype):
        # we must have a response with one of the RDF datatype headers
        # TODO: review all the mimetypes handled by rdflib
        formats = {
            'text/turtle': 'turtle',
            'text/ntriples': 'nt',
            'text/n3': 'nt',
            'application/rdf+xml': 'xml',
            'application/rdf+json': 'json-ld',
        }

        return formats[mimetype]

    def valid_rdf(self, http_response):
        # this parsing will raise an rdflib error if the RDF is broken
        g = rdflib.Graph().parse(
            StringIO(http_response.content),
            format=self.get_rdflib_rdf_format(http_response.headers.get['Content-Type'])
        )

        return g

    def valid_skos(self, rdf_graph):
        pass

    def get_concept_info(self):
        prefLabel = 'nick'
        return {
            'skos_prefLabel': prefLabel
        }


class CliValuesValidator:
    # the key values that we allow to formulate SKOS queries with
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

    def is_a_uri(self, uri_candidate):
        """
        Validates a string as a URI

        :param uri_candidate: string
        :return: True or False
        """
        # https://gist.github.com/dperini/729294
        URL_REGEX = re.compile(
            u"^"
            # protocol identifier
            u"(?:(?:https?|ftp)://)"
            # user:pass authentication
            u"(?:\S+(?::\S*)?@)?"
            u"(?:"
            # IP address exclusion
            # private & local networks
            u"(?!(?:10|127)(?:\.\d{1,3}){3})"
            u"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
            u"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
            # IP address dotted notation octets
            # excludes loopback network 0.0.0.0
            # excludes reserved space >= 224.0.0.0
            # excludes network & broadcast addresses
            # (first & last IP address of each class)
            u"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
            u"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
            u"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
            u"|"
            # host name
            u"(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)"
            # domain name
            u"(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*"
            # TLD identifier
            u"(?:\.(?:[a-z\u00a1-\uffff]{2,}))"
            u")"
            # port number
            u"(?::\d{2,5})?"
            # resource path
            u"(?:/\S*)?"
            u"$"
            , re.UNICODE
        )
        return re.match(URL_REGEX, uri_candidate)


class RdfValuesValidator:
    # allowed Content-Types for URI dereferencing results
    pass
