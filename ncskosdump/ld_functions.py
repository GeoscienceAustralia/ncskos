'''
Class definition for ConceptFetcher to to perform SKOS vocabulary lookups

Created on 30 Sep 2016

@author: Nicholas Car
'''
import re
from StringIO import StringIO
import logging

# Turn off logging for anything we didn't write - it's just plain annoying
# N.B: This needs to be before the import for requests and rdflib despite whatever pep8 might whinge about
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('rdflib').setLevel(logging.WARNING)

import requests
import rdflib

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Initial logging level for this module

class ConceptFetcher(object):
    '''
    Class definition for ConceptFetcher to to perform SKOS vocabulary lookups
    '''
    # Dict of supported mimetypes
    VALID_MIMETYPES = {'text/turtle': 'turtle',
                       'text/ntriples': 'nt',
                       'text/nt': 'nt',
                       'text/n3': 'nt',
                       'application/rdf+xml': 'rdf',
                       'application/rdf+json': 'json-ld'
                       }
    
    def __init__(self, skos_params, debug=False):
        """ConceptFetcher constructor
        :param skos_params: dict containing SKOS options
        :param debug: Boolean debug output flag
        """
        self.set_debug(debug) # Turn debug output on or off as required
        self.uri = None
        self.rdf_graph = None
        
        if not self.valid_command_line_args(skos_params):
            exit()
            
        self.skos_params = skos_params
        
        self.local_cache_dict = {}

    def setup_rdf_graph(self, uri):
        '''Function to set up self.rdf_graph if the URI is new
        '''
        if self.uri != uri:
            self.parse_rdf(self.dereference_uri(uri)) 
            self.uri = uri
               
    def valid_command_line_args(self, skos_params):
        """Ensure that we receive valid command line args
        :param skos_params: dict containing SKOS options
        :return: boolean
        """
        # ensure only allowed k/v pairs exist
        for k in skos_params.keys():
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
            raise Exception('A broader argument, if present, must be either "true" or "false"')

        # if narrower param is present, must be a boolean
        if skos_params.get('narrower') and type(skos_params.get('narrower')) != bool:
            raise Exception('A narrower argument, if present, must be either "true" or "false"')

        # if we've made it this far, the args are valid
        return True

    def valid_skos_concept_uri(self, potential_uri):
        if not CliValuesValidator.is_a_uri(potential_uri):
            raise Exception('The skos_concept_uri netCDF header value {} is not a valid URI.', potential_uri)

        return True

    def dereference_uri(self, uri):
        """Get the RDF data for the Concept via dereferencing the given URI

        :param uri: a valid URI for a SKOS Concept
        :return: RDF data
        """
        logger.debug('Dereferencing URI = %s', uri)
        # get the RDF for this concept by dereferencing the URI
        # TODO: enable redirect following based on the status code (i.e. perhaps 303 & 302 but not 301 or whatever)
        s = requests.Session()
        s.headers['Accept'] = 'text/turtle,application/rdf+xml'
        s.max_redirects = 3  # TODO: review this magic number
        r = s.get(uri)
        # fail if not 20x status code
        r.raise_for_status()

        logger.debug('RDF Data = %s', r)
        return r

    def get_rdflib_rdf_format(self, mimetype):
        # we must have a response with one of the RDF datatype headers
        # TODO: review all the mimetypes handled by rdflib
        logger.debug('mimetype = %s', mimetype)
        
        rdf_format = ConceptFetcher.VALID_MIMETYPES.get(mimetype.split(';')[0]) # Only look at string before semicolon

        if rdf_format is None:
            raise Exception('%s does not represent a valid rdflib RDF format' % mimetype)
        
        logger.debug('RDF Format = %s', rdf_format)
        return rdf_format

    def parse_rdf(self, http_response):
        # this parsing will raise an rdflib error if the RDF is broken
        logger.debug('http_response.content = %s', http_response.content)
        self.rdf_graph = rdflib.Graph().parse(StringIO(http_response.content),
                                      format=self.get_rdflib_rdf_format(http_response.headers.get('Content-Type'))
                                      )

        logger.debug('graph = %s', self.rdf_graph)

    def valid_skos(self, uri):
        """Here we are NOT validating SKOS per se, we are only validating the minimum requirement for a Concept label
        retrieval

        :param uri: Potential SKOS URI
        :return: bool
        """
        self.setup_rdf_graph(uri)
               
        # is there a skos:Concept declaration for the URI and does it have a skos:prefLabel?
        q = '''
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            ASK
            WHERE {
                ?c ?p ?o .
                <''' + uri + '''> a skos:Concept .
                ?c skos:prefLabel ?pl .
            }
        '''
        logger.debug('valid_skos query = %s', q)
        qres = self.rdf_graph.query(q)
        logger.debug('valid_skos result = %s', list(qres))
        
        return bool(qres)

    def get_prefLabel(self, uri, lang='en'):
        """Get the prefLabel for the given Concept URI

        :param uri: a valid URI for a SKOS Concept
        :return: string prefLabel
        :return: string lang
        """
        self.setup_rdf_graph(uri)
            
        pl = None
        if lang is None: lang = 'en'  # in case some absolute drongo sets the lang to None
        
        q = '''
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            SELECT ?pl
            WHERE {
                ?c ?p ?o .
                <%(uri)s> a skos:Concept .
                ?c skos:prefLabel ?pl .

                FILTER (lang(?pl) = "%(lang)s")
            }
        ''' % {'uri': uri, 'lang': lang}
        
        logger.debug('get_prefLabel query = %s', q)
        qres = self.rdf_graph.query(q)
        logger.debug('get_prefLabel result = %s', list(qres))
        
        for row in qres:
            pl = row['pl']
        if pl is not None:
            return str(pl), lang
        else:
            raise Exception('Concept does not have a prefLabel in the language you chose ({0})'.format(lang))

    def get_altLabels(self, uri):
        """Get the comma separated list of altLabels for the given Concept URI

        :param uri: a valid URI for a SKOS Concept
        :return: string containing altLabels as a comma separated list
        """
        self.setup_rdf_graph(uri)

        als = []
        q = '''
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            SELECT ?al
            WHERE {
                <%(uri)s> a skos:Concept ;
                    skos:altLabel ?al .
            }
        ''' % {'uri': uri}
        
        logger.debug('get_altLabels query = %s', q)
        qres = self.rdf_graph.query(q)
        logger.debug('get_altLabels result = %s', list(qres))
        
        for row in qres:
            als.append(row['al'])
        if als is not None:
            return sorted(als)
        else:
            raise Exception('Concept does not have altLabels')

    def get_narrower(self, uri):
        """Get the comma separated list of narrower concepts for the given Concept URI

        :param uri: a valid URI for a SKOS Concept
        :return: string containing narrower concepts as a comma separated list
        """
        self.setup_rdf_graph(uri)
            
        narrower = []
        q = '''
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            SELECT ?n
            WHERE {
                <%(uri)s> skos:narrower+ ?n .
            }
        ''' % {'uri': uri}
        
        logger.debug('get_narrower query = %s', q)
        qres = self.rdf_graph.query(q)
        logger.debug('get_narrower result = %s', list(qres))
        
        for row in qres:
            narrower.append(row['n'])
        if narrower is not None:
            return sorted(narrower)
        else:
            raise Exception('Concept does not have any narrower Concepts')

    def get_broader(self, uri):
        """Get the comma separated list of broader concepts for the given Concept URI

        :param uri: a valid URI for a SKOS Concept
        :return: string containing broader concepts as a comma separated list
        """
        self.setup_rdf_graph(uri)
            
        broader = []
        q = '''
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            SELECT ?b
            WHERE {
                <%(uri)s> skos:broader+ ?b .
            }
        ''' % {'uri': uri}
        
        logger.debug('get_broader query = %s', q)
        qres = self.rdf_graph.query(q)
        logger.debug('get_broader result = %s', list(qres))
        
        for row in qres:
            broader.append(row['b'])
        if broader is not None:
            return sorted(broader)
        else:
            raise Exception('Concept does not have any broader Concepts')

    def get_results(self, uri):
        """Get the full SKOS results for the given Concept URI

        :param uri: a valid URI for a SKOS Concept
        :return: dict containing all results specified in self.skos_params
        """
        if uri in self.local_cache_dict.keys():
            logger.debug('URI %s found in cache' % uri)
            return self.local_cache_dict[uri]

        if not self.valid_skos_concept_uri(uri):
            exit()
            
        if not self.valid_skos(uri):
            exit()

        # get the prefLabel regardless of options set
        prefLabel, lang = self.get_prefLabel(uri, lang=self.skos_params.get('lang'))
        results = {'skos_prefLabel' + '_' + lang: prefLabel}

        # only get this if the arg altLabels=true
        if self.skos_params.get('altLabels'):
            results['skos_altLabels'] = str(', '.join(self.get_altLabels(uri)))

        # only get this if the arg narrower=true
        if self.skos_params.get('narrower'):
            results['skos_narrower'] = str(', '.join(self.get_narrower(uri)))

        # only get this if the arg broader=true
        if self.skos_params.get('broader'):
            results['skos_broader'] = str(', '.join(self.get_broader(uri)))

        self.local_cache_dict[uri] = results
        
        return results


    def get_debug(self): 
        return self._debug
    
    def set_debug(self, value): 
        self._debug = value
        if self._debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        
    debug = property(get_debug, set_debug, doc='Boolean debug output flag')
    
    
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

    @staticmethod
    def is_a_uri(uri_candidate):
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
