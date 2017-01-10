import requests
from StringIO import StringIO
import rdflib


class ConceptHierarchy2(object):
    """
    Builds a Concept's hierarchy by following all the URIs it can find for it:
        - broader, all the way up in the single vocab
        - narrower, all the way down
        - if no top found
            - from the ConceptScheme, from each topConceptOf until a recognised URI is found
    """
    # get starting Concept's graph
    # if topConceptOf
    #   flag top
    # else
    #   find top concepts, cache their URIs
    #
    # get all broaders (parallel)
    # for each broader
    #   get graph
    #       if not still in voc
    #           exit subproc
    #       elif topConcept recognised or declared
    #          flag top
    #       else:
    #           get all broaders (parallel)
    #
    # get all narrowers (parallel)
    #   get graph
    #       get all narrowers (parallel)
    #
    # if no top
    #   resolve ConceptScheme
    #   get topConceptOf (serial)
    #   if narrower
    #       if already seen
    #           hierarchy complete
    #       else
    #           keep looking
    VALID_MIMETYPES = {
        'text/turtle': 'turtle',
        'text/ntriples': 'nt',
        'text/nt': 'nt',
        'text/n3': 'nt',
        'application/rdf+xml': 'rdf',
        'application/rdf+json': 'json-ld'
    }

    def __init__(self, initial_concept_uri):
        self.g = None
        self.initial_concept_uri = initial_concept_uri
        # self.hierarchy = self.make_hierarchy(self.initial_concept_uri)
        self.add_uri_rdf_to_graph(initial_concept_uri)
        self.get_broader(initial_concept_uri)

    def make_hierarchy(self, initial_concept_uri):
        pass

    def add_uri_rdf_to_graph(self, uri):
        rdf_response = self.dereference_uri(uri)
        self.g += self.parse_rdf_return_graph(rdf_response)

    def dereference_uri(self, uri):
        """Get the RDF data for the Concept via dereferencing the given URI

        :param uri: a valid URI for a SKOS Concept
        :return: RDF data
        """
        accepted_mime_types = ''
        for mimetype in self.VALID_MIMETYPES.iterkeys():
            accepted_mime_types += mimetype + ', '
        r = requests.get(uri, allow_redirects=True, headers={'Accept': accepted_mime_types})
        r.raise_for_status()

        return r

    def get_rdflib_rdf_format(self, content_type_header):
        """
        Gets the rdflib RDF format relevant for a requests response object
        :param requests_response: a requests module response object
        :return: string, one of rdflib's RDF formats
        """
        if content_type_header.split(';')[0] not in self.VALID_MIMETYPES:
            raise Exception(
                '%s does not represent a valid rdflib RDF format' % content_type_header)
        else:
            return self.VALID_MIMETYPES[content_type_header.split(';')[0]]

    def parse_rdf_return_graph(self, http_response):
        # this parsing will raise an rdflib error if the RDF is broken
        return rdflib.Graph().parse(
            StringIO(http_response.content),
            format=self.get_rdflib_rdf_format(
                http_response.headers.get('Content-Type'))
        )

    def get_broader(self, uri):
        pass

    def get_narrower(self, uri):
        pass