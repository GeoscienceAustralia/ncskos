"""
Created on 16Dec.,2016

@author: Alex Ip
"""
import os
from ncskosdump.ld_functions import ConceptFetcher

class Concept(object):
    '''
    Simple class to hold Concept attributes.
    '''
    def __init__(self,
                 concept_uri,
                 prefLabel=None,
                 altLabels=None, # List of altLabel strings
                 unresolved=True
                 ):
        '''
        Constructor for simple Concept class. Everything is public.
        '''
        self.uri = concept_uri
        
        # Assume URI is unresolved for initial object
        label = 'Unresolved URI ' + os.path.basename(concept_uri)
        self.prefLabel = prefLabel or label 
        self.altLabels = altLabels or [label]
        self.unresolved = unresolved

        self.broader = []
        self.narrower = []
        
    def update(self, concept_results, lang='en'):
        '''
        Function to update concept attributes from concept_fetcher.get_results() result dict
        '''
        if concept_results:
            self.prefLabel = (concept_results.get('skos__prefLabel_' + lang) or 
                              concept_results.get('skos__prefLabel_en') + ' (English)'
                              )
            self.altLabels = [alt_label.strip() 
                              for alt_label in concept_results['skos__altLabels'].split(',') 
                              if alt_label]
    
            self.unresolved = False

    def add_related_concept(self, related_concept, relationship='narrower'):
        '''
        Function to add new narrower or broader concept
        '''
        relationship_list = getattr(self, relationship)                             
        assert type(relationship_list) == list, 'Unrecognised relationship "%s"' % relationship
        
        if related_concept not in relationship_list:
            relationship_list.append(related_concept)

    def get_related_concepts(self, relationship='narrower'):
        '''
        Recursive function to return list of all narrower or broader concepts for concept. 
        '''
        relationship_list = getattr(self, relationship)                             
        assert type(relationship_list) == list, 'Unrecognised relationship "%s"' % relationship
        
        related_concepts = list(relationship_list)
        for related_concept in relationship_list:
            related_concepts += related_concept.get_related_concepts(relationship)                         
        return related_concepts
    
    
    def get_sibling_concepts(self):
        '''
        Function to return all sibling concepts (narrower concepts of broader concepts)
        '''
        sibling_concept_list = []
        for broader_concept in self.broader: # Allow for multiple "broader" concepts
            sibling_concept_list += broader_concept.narrower
        return sibling_concept_list
        
        
class ConceptHierarchy(object):
    """
    Class to track broader/narrower heirarchy of concepts
    """
    def get_concept_from_uri(self, concept_uri, refresh_cache=False):
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
        
        # Check registry to see if we already have it cached
        concept = self.concept_registry.get(concept_uri) 
        
        if concept:
            if self.verbose:
                print 'Found concept in cache for URI %s' % concept_uri
            if not refresh_cache:
                return concept
        
        concept = Concept(concept_uri) # create new Concept object (assume unresolved)
        if self.verbose:
            print 'Resolving concept_uri = %s' % concept_uri
        
        try:
            concept_results = self.concept_fetcher.get_results(concept_uri)  # Look up URI
        except Exception as e:
            print 'WARNING: Unable to resolve URI %s: %s' % (concept_uri, e.message)                       
            self.concept_registry[concept_uri] = concept            
            return concept 
            
        concept.update(concept_results, lang=self.lang)
            
        self.concept_registry[concept_uri] = concept
        
        # Recursively populate narrower & broader lists if required
        if self.broader:
            concept.broader += [self.get_concept_from_uri(uri.strip()) for uri in (concept_results.get('skos__broader') or '').split(',') if uri]
            
            if not self.narrower:  # Update narrower list in broader concept(s) as required
                for broader_concept in concept.broader:
                    broader_concept.add_related_concept(concept, 'narrower')
             
        if self.narrower:
            concept.narrower += [self.get_concept_from_uri(uri.strip()) for uri in (concept_results.get('skos__narrower') or '').split(',') if uri]

            if not self.broader: # Update broader list in narrower concept(s) as required
                for narrower_concept in concept.narrower:
                    narrower_concept.add_related_concept(concept, 'broader')
                            
        return concept
    
    def get_top_concepts(self):
        '''
        Function to return list of concepts without any "broader" concepts
        '''
        return [concept for concept in self.concept_registry.values() if not concept.broader]
    
    def get_bottom_concepts(self):
        '''
        Function to return list of concepts without any "narrower" concepts recorded. 
        Note: Narrower concepts may exist in vocab, but will only be recorded if their URI is resolved
        '''
        return [concept for concept in self.concept_registry.values() if not concept.narrower]
    
    def get_concept_by_altlabel(self, altlabel):
        '''
        Function to return list of concepts with matching altLabel (case insensitive match). 
        '''
        return [concept for concept in self.concept_registry.values() 
                if altlabel.lower() in [concept_altlabel.lower() 
                                        for concept_altlabel in concept.altLabels]
                ]
    
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
            self.get_concept_from_uri(initial_concept_uri)  # Build tree around initial URI

    def print_concept_tree(self, concept, level=0):
        '''
        Recursive function to print indented concept subtree
        '''
        if concept is not None:
            print '\t' * level + concept.prefLabel
            for narrower_concept in concept.narrower:
                self.print_concept_tree(narrower_concept, level+1)

    def get_unresolved_concepts(self):
        '''
        Function to return a list of all unresolved concepts
        '''
        return [concept for concept in self.concept_registry.values() 
                if concept.unresolved
                ]

    def retry_unresolved_uris(self):
        '''
        Function to try to retry failed web queries and update all unresolved URIs
        '''
        for unresolved_concept in self.get_unresolved_concepts():
            self.get_concept_from_uri(unresolved_concept.uri, refresh_cache=True)
            
     
def main():
    '''
    Main function for quick-and-dirty testing. May be removed later
    '''
    concept_hierarchy = ConceptHierarchy(
        'http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature',
        narrower=True # Build complete hierarchy from top to bottom
    )

    for top_concept in [concept for concept in concept_hierarchy.get_top_concepts()]:
        concept_hierarchy.print_concept_tree(top_concept)
    

if __name__ == '__main__':
    main()
