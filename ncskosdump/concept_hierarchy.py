"""
Created on 16Dec.,2016

@author: Alex Ip
"""
import os
from ncskosdump.ld_functions import ConceptFetcher


class ConceptHierarchy(object):
    """
    Class to track broader/narrower heirarchy of concepts
    """
    def get_concept(self, concept_uri):
        """
        Recursive function to return dict containing altLabels and lists of broader and narrower concepts
        for the specified concept_uri. Note that "broader" concepts are searched recursively up to the top concept, 
        while "narrower" concepts are only updated as required as narrower concept URIs are encountered.
        Unresolved URIs will have an artificial top-level concept created.
        :param concept_uri: URI for concept.
        :param verbose: Boolean flag to produce extra output
        :return dict containing information for concept read from cache or from SKOS query
            dict keys are: ['prefLabel', 'uri', 'altLabels', 'broader', 'narrower']
        """
        if not concept_uri:
            return None
        
        concept = self.concept_registry.get(concept_uri)  # Check registry to see if we already have it
        
        if concept:
            if self.verbose:
                print 'Found concept in cache for URI %s' % concept_uri
            return concept
        
        if self.verbose:
            print 'Resolving concept_uri = %s' % concept_uri
        
        try:
            concept_results = self.concept_fetcher.get_results(concept_uri)  # Look up URI
        except Exception as e:
            print 'WARNING: Unable to resolve URI %s: %s' % (concept_uri, e.message)
            
            # Create "fake" concept object with no broader/narrower concepts
            label = 'Unresolved URI ' + os.path.basename(concept_uri)
            concept = {'prefLabel': label,
                       'uri': concept_uri,
                       'altLabels': [label,],
                       'broader':[],
                       'narrower': []
                       }
            
            self.concept_registry[concept_uri] = concept
            
            return concept 
            
        concept = {'prefLabel': (concept_results.get('skos__prefLabel_' + self.lang) or 
                                 concept_results.get('skos__prefLabel_en') + ' (English)'
                                 ),
                   'uri': concept_uri,
                   'altLabels': [alt_label.strip() 
                                 for alt_label in concept_results['skos__altLabels'].split(',') 
                                 if alt_label],
                   'broader': [],
                   'narrower': []
                   }
            
        self.concept_registry[concept_uri] = concept
        
        # Recursively populate narrower & broader lists if required
        if self.broader:
            concept['broader'] += [self.get_concept(uri.strip()) for uri in (concept_results.get('skos__broader') or '').split(',') if uri]
            
            if not self.narrower:  # Update narrower list in broader concept(s) as required
                for broader_concept in concept['broader']:
                    if concept not in broader_concept['narrower']:
                        broader_concept['narrower'].append(concept)
             
        if self.narrower:
            concept['narrower'] += [self.get_concept(uri.strip()) for uri in (concept_results.get('skos__narrower') or '').split(',') if uri]

            if not self.broader: # Update broader list in narrower concept(s) as required
                for narrower_concept in concept['narrower']:
                    if concept not in narrower_concept['broader']:
                        narrower_concept['broader'].append(concept)
                            
        return concept
    
    def get_top_concepts(self):
        '''
        Function to return concepts without any "broader" concepts
        '''
        return [concept for concept in self.concept_registry.values() if not concept['broader']]
    
    def get_bottom_concepts(self):
        '''
        Function to return concepts without any "narrower" concepts recorded. 
        Note: Narrower concepts may exist in vocab, but will only be recorded if their URI is resolved
        '''
        return [concept for concept in self.concept_registry.values() if not concept['narrower']]
    
    def __init__(self, initial_concept_uri=None, lang=None, broader=True, narrower=False, verbose=False):
        """
        Constructor for class ConceptHierarchy
        Note: Need at least one of "narrower" or "broader" specified as True in order to build concept trees
        :param initial_concept_uri: Optional initial URI from which to obtain "broader" concepts to build initial tree
        :param lang: Optional two-character ISO 639-1:200 language code. Defaults to 'en'
        :param broader: Boolean flag dictating whether concept trees should be recursively populated up to top concept. 
            Defaults to True
        :param narrower: Boolean flag dictating whether concept trees should be recursively populated down to bottom concepts. 
            Defaults to False
        """
        assert narrower or broader, 'Need at least one of "broader" or "narrower" set to True in order to build concept trees'
        
        self.lang = lang or 'en'
        self.narrower = narrower
        self.broader = broader
        self.verbose = verbose
        
        skos_option_dict = {'altLabels': True, 
                            'narrower': narrower, 
                            'broader': broader,
                            'lang': lang
                            }           
        self.concept_fetcher = ConceptFetcher(skos_option_dict)
        
        self.concept_registry = {}
    
        if initial_concept_uri:
            self.get_concept(initial_concept_uri)  # Build tree around initial URI

    def print_concept_tree(self, concept, level=0):
        """Recursive function to print indented concept subtree"""
        if concept is not None:
            print '\t' * level + concept['prefLabel']
            for narrower_concept in concept['narrower']:
                self.print_concept_tree(narrower_concept, level+1)


def main():
    '''
    Main function for quick-and-dirty testing. May be removed later
    '''
    concept_hierarchy = ConceptHierarchy(
        'http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature'
    )

    for top_concept in [concept for concept in concept_hierarchy.get_top_concepts()]:
        concept_hierarchy.print_concept_tree(top_concept)
    

if __name__ == '__main__':
    main()
