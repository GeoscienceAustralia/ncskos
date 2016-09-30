'''
Created on 30 Sep 2016

@author: Alex Ip
'''

import netCDF4
import sys
import re
import os
import logging
import subprocess
import tempfile

# Set handler for root logger to standard output
console_handler = logging.StreamHandler(sys.stdout)
#console_handler.setLevel(logging.INFO)
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(console_formatter)
logging.root.addHandler(console_handler)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # Initial logging level for this module

class NCLDDump(object):
    ATTRIBUTE_NAME = 'skos_concept_uri'
    MAX_MEM = 1000000000 # 1GB?
    
    def __init__(self, arguments=None):
        '''
        NCLDDump constructor
        '''
        if arguments is not None:
            for line in self.process_ncdump(arguments):
                print line
            
    def resolve_skos_uri(self, uri, skos_options_dict=None):
        '''
        Function to resolve Linked Data URI and return string result
        '''
        skos_options_dict = skos_options_dict or {}
        
        #TODO: Replace stub with Nick's link resolving code
        return 'Freddo Frog'

    def process_ncdump(self, arguments):
        '''
        Function to perform link resolution and text substitution on ncdump output
        @param arguments: List of command line arguments
        
        Returns:
            ncdump_arguments: List of ncdump arguments
            skos_option_dict: Dict containing <key>:<value> SKOS options
        '''
        def get_skos_args(arguments):
            '''
            Helper function to split SKOS options from ncdump arguments
            '''
            key_value_regex = re.compile('(\w+)=(.*)')
            ncdump_arguments = []
            skos_option_dict = {}
            
            skos_args = False
            for arg in arguments:
                if skos_args:
                    if arg[0] == '-': # New switch
                        skos_args = False # Keep processing non-SKOS arg (no "continue")
                    else:
                        key_value_match = re.search(key_value_regex, arg)
                        assert key_value_match is not None, 'SKOS options must be expressed as <key>=<value>'
                        key = key_value_match.group(1).strip()
                        value = key_value_match.group(2).strip()
                        logger.debug('key = %s, value = %s', key, value)
                        
                        # Perform basic typecasting from string to float or bool
                        try:
                            value = float(value)
                        except ValueError:
                            if re.match('True', value, re.I):
                                value = True
                            elif re.match('False', value, re.I):
                                value = False
                        
                        skos_option_dict[key] = value
                        continue
                        
                elif re.match('--skos', arg, re.I) is not None:
                    skos_args = True
                    continue
                
                # Any non-SKOS argument is for ncdump
                ncdump_arguments.append(arg)
                    
            return ncdump_arguments, skos_option_dict        
               
        ncdump_arguments, skos_option_dict = get_skos_args(arguments)
        logger.debug('ncdump_arguments = %s', ncdump_arguments)
        logger.debug('skos_option_dict = %s', skos_option_dict)
        
        # Example: '    time:concept_uri = "http://pid.geoscience.gov.au/def/voc/netCDF-ld-example-tos/time" ;'
        attribute_regex_string = '^\s*(\w+):' + NCLDDump.ATTRIBUTE_NAME + '\s*=\s*"(http(s*)://.*)"\s*;\s*$' 
        logger.debug('attribute_regex_string = %s', attribute_regex_string)
        attribute_regex = re.compile(attribute_regex_string)
        
        ncdump_command = ['ncdump'] + ncdump_arguments
        logger.debug('ncdump_command = "%s"', ' '.join(ncdump_command))
        
        input_spool = tempfile.SpooledTemporaryFile(max_size=NCLDDump.MAX_MEM, 
                                                   mode='w+', 
                                                   bufsize=-1,
                                                   #suffix="", 
                                                   #prefix=template, 
                                                   #dir=None
                                                   )
        
        output_spool = tempfile.SpooledTemporaryFile(max_size=NCLDDump.MAX_MEM, 
                                                   mode='w+', 
                                                   bufsize=-1,
                                                   #suffix="", 
                                                   #prefix=template, 
                                                   #dir=None
                                                   )
        
        input_spool.write(subprocess.check_output(ncdump_command))
        input_spool.seek(0)
        
        for line in input_spool.readlines():
            logger.debug('line = %s', line)
            
            attribute_match = re.match(attribute_regex, line)
            if attribute_match is not None:
                variable_name = attribute_regex.group(1)
                uri = attribute_regex.group(2)
                logger.debug('variable_name = %s, uri = %s', variable_name, uri)
                
                attribute_value = self.resolve_skos_uri(uri, skos_option_dict)
                logger.debug('attribute_value = %s', attribute_value)
                
                line.replace(uri, attribute_value)
                
            output_spool.write(line)  
         
        input_spool.close()
        return output_spool
