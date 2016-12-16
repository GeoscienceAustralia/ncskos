'''
Created on 16Dec.,2016

@author: Alex Ip
'''
from ncskosdump.ld_functions import ConceptFetcher

class ConceptHierarchy(object):
    '''Class to track broader/narrower heirarchy of concepts'''
    # Always ask for narrower, broader and altlabels - only lang is optional
    skos_option_dict = {'altLabels': True, 'narrower': True, 'broader': True}
    concept_fetcher = ConceptFetcher(skos_option_dict)
    
    concept_registry = {}
    
    def get_concept(self, concept_uri):
        '''Recursive function to return dict containing altLabels and lists of broader and narrower concepts
        for the specified concept_uri'''
        
        concept = ConceptHierarchy.concept_registry.get(concept_uri) # Check registry to see if we already have it
        
        if concept:
            return concept
        
        try:
            concept_results = ConceptHierarchy.concept_fetcher.get_results(concept_uri) # Look up URI
        except:
            return None
        
        concept = {'prefLabel': concept_results['skos__prefLabel_en'],
                   'uri': concept_uri,
                   'altLabels': [alt_label.strip() for alt_label in concept_results['skos__altLabels'].split(',') if alt_label]}
                                   
        for key, uri_list in {'narrower': concept_results.get('skos__narrower') or '', 
                              'broader': concept_results.get('skos__broader') or ''
                              }.iteritems():
            concept[key] = [self.get_concept(uri.strip()) for uri in uri_list.split(',') if uri]

        ConceptHierarchy.concept_registry[concept_uri] = concept
        
        # Hack to fix up missing broader concepts by inferring them from narrower concepts
        for narrower_concept in concept['narrower']:
            narrower_concept['broader'].append(concept)
        
        return concept
    
    def get_top_concepts(self):
        return [concept for concept in ConceptHierarchy.concept_registry.values() if not concept['broader']]
    
    def get_bottom_concepts(self):
        return [concept for concept in ConceptHierarchy.concept_registry.values() if not concept['narrower']]
    
    def __init__(self, initial_concept_uri=None):
        '''Constructor'''
        if initial_concept_uri:
            self.get_concept(initial_concept_uri) # Build tree around initial URI

    def print_concept_tree(self, concept, level=0):
        '''Recursive function to print indented concept subtree'''
        print '\t' * level + concept['prefLabel']
        for narrower_concept in concept['narrower']:
            self.print_concept_tree(narrower_concept, level+1)

def main():
    concept_hierarchy = ConceptHierarchy('http://pid.geoscience.gov.au/def/voc/netCDF-LD-eg-ToS/sea_surface_temperature')

    for top_concept in [concept for concept in concept_hierarchy.get_top_concepts()]:
        concept_hierarchy.print_concept_tree(top_concept)
    

if __name__ == '__main__':
    main()