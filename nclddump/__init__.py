import netCDF4
import sys
import re
import os
import logging
import subprocess
import tempfile

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # Initial logging level for this module

class NCLDDump(object):
    ATTRIBUTE_NAME = 'skos _concept_uri'
    MAX_MEM = 1000000000 # 1GB?
    
    def __init__(self, ncdump_arguments=None):
        '''
        NCLDDump constructor
        '''
        self.ncdump_arguments = ncdump_arguments
        
        if ncdump_arguments is not None:
            for line in self.process_ncdump(ncdump_arguments):
                print line
            
    def resolve_uri(self, uri):
        '''
        Function to resolve Linked Data URI and return string result
        '''
        #TODO: Replace stub with Nick's link resolving code
        return 'Freddo Frog'

    def process_ncdump(self, ncdump_arguments=None):
        '''
        Function to perform link resolution and text substitution on ncdump output
        '''
        ncdump_arguments = ncdump_arguments or self.ncdump_arguments
        logger.debug('ncdump_arguments = %s', ncdump_arguments)
        
        # Example: '    time:concept_uri = "http://pid.geoscience.gov.au/def/voc/netCDF-ld-example-tos/time" ;'
        attribute_regex_string = '^\s*(\w+):' + NCLDDump.ATTRIBUTE_NAME + '\s*=\s*"(http(s*)://.*)"\s*;\s*$' 
        logger.debug('attribute_regex_string = %s', attribute_regex_string)
        attribute_regex = re.compile(attribute_regex_string)
        
        ncdump_command = ['ncdump'] + ncdump_arguments
        
        input_spool = tempfile.SpooledTemporaryFile(max_size=NCLDDump.MAX_MEM, 
                                                   mode='w+b', 
                                                   bufsize=-1,
                                                   #suffix="", 
                                                   #prefix=template, 
                                                   #dir=None
                                                   )
        
        output_spool = tempfile.SpooledTemporaryFile(max_size=NCLDDump.MAX_MEM, 
                                                   mode='w+b', 
                                                   bufsize=-1,
                                                   #suffix="", 
                                                   #prefix=template, 
                                                   #dir=None
                                                   )
        
        input_spool.write(subprocess.check_output(ncdump_command))
        
        
        for line in input_spool.readlines():
            logger.debug('line = %s', line)
            
            attribute_match = re.match(attribute_regex, line)
            if attribute_match is not None:
                variable_name = attribute_regex.group(1)
                uri = attribute_regex.group(2)
                logger.debug('variable_name = %s, uri = %s', variable_name, uri)
                
                attribute_value = self.resolve_uri(uri)
                logger.debug('attribute_value = %s', attribute_value)
                
                line.replace(uri, attribute_value)
                
            output_spool.write(line)  
         
        input_spool.close()
        return output_spool
    
def main():
    NCLDDump(sys.argv[1:])
    
if __name__ == '__main__':
    main()