"""
Class definition for NcSKOSDump to implement prototype ncskosdump command
Wraps ncdump to perform SKOS vocabulary lookups and substitute these into the
CDL or XML output

Note: This utility requires that the netCDF command line utilities be
installed.
These utilities are available from:
http://www.unidata.ucar.edu/software/netcdf/docs/getting_and_building_netcdf.html

Created on 30 Sep 2016

@author: Alex Ip
"""

import sys
import re
import os
import logging
import subprocess
import tempfile
from lxml import etree
from distutils.util import strtobool
from ld_functions import ConceptFetcher

# Set handler for root logger to standard output if no handler exists
if not logging.root.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    logging.root.addHandler(console_handler)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Initial logging level for this module


class NcSKOSDump(object):
    """
    Class definition for NcSKOSDump to implement prototype ncskosdump command
    Wraps ncdump to perform SKOS vocabulary lookups and substitute these into
    the CDL output
    """
    SKOS_ATTRIBUTE = 'skos_concept_uri'  # Attribute name for SKOS URIs
    MAX_MEM = 1000000000  # Limit before switching from stringIO to file (1GB?)

    def __init__(self, arguments=None, debug=False):
        """
        NcSKOSDump constructor
        :param arguments: optional list of ncdump args with additional
        optional "--skos <skos_option>=<value>..." args
        :param debug: Boolean debug output flag
        """
        self._error = None
        self.concept_fetcher = None

        self.set_debug(debug)  # Turn debug output on or off as required

        # Process and print results to standard output if arguments have been
        # provided
        if arguments is not None:
            for line in self.process_ncdump(arguments):
                print line.replace(os.linesep, '')

    def get_skos_args(self, arguments):
        """
        Helper function to split SKOS options from ncdump arguments
        :param arguments: ncdump args with optional
            "--skos <skos_option>=<value> <skos_option>=<value>..." args

        :return: ncdump_arguments: List of ncdump args WITHOUT optional
            "--skos <skos_option>=<value> <skos_option>=<value>..." args
        :return: skos_option_dict: Dict containing <key>:<value> SKOS options
        """
        key_value_regex = re.compile('(\w+)=(.*)')
        ncdump_arguments = []
        skos_option_dict = {}

        skos_args = False
        for arg in arguments:
            arg = arg.strip()  # This should deal with any stray EOL characters
            if skos_args:
                if arg[0] == '-':  # New switch
                    # Keep processing non-SKOS arg (no "continue")
                    skos_args = False
                else:
                    key_value_match = re.search(key_value_regex, arg)
                    # SKOS options must be expressed as "<key>=<value>"
                    if key_value_match is not None:
                        key = key_value_match.group(1).strip()
                        value = key_value_match.group(2).strip()
                        logger.debug('key = %s, value = %s', key, value)

                        # Perform basic typecasting from string to float or
                        # bool
                        try:
                            value = float(value)
                        except ValueError:
                            try:
                                value = bool(strtobool(value))
                            except ValueError:
                                pass  # No change to string value

                        skos_option_dict[key] = value
                        continue
                    else:  # arg must be filename - add to ncdump_arguments
                        skos_args = False

            elif re.match('--skos', arg, re.I) is not None:
                skos_args = True
                continue

            # Any non-SKOS argument is for ncdump
            ncdump_arguments.append(arg)

        return ncdump_arguments, skos_option_dict

    def process_ncdump(self, arguments):
        """
        Function to perform skos URI resolution and text substitution on ncdump
        output
        :param arguments: ncdump arguments with optional
            "--skos <skos_option>=<value>..." arguments
        :return: file-like object containing modified ncdump output
        """
        self._error = None
        ncdump_arguments, skos_option_dict = self.get_skos_args(arguments)
        logger.debug('ncdump_arguments = %s', ncdump_arguments)
        logger.debug('skos_option_dict = %s', skos_option_dict)

        xml_output = (
            len([arg for arg in ncdump_arguments
                 if re.match('\-\w*x\w*', arg)]) > 0)

        if (not self.concept_fetcher or
                self.concept_fetcher.skos_params != skos_option_dict):
            self.concept_fetcher = ConceptFetcher(skos_option_dict, self.debug)

        ncdump_command = ' '.join(['ncdump'] + ncdump_arguments)
        logger.debug('ncdump_command = "%s"', ncdump_command)

        input_spool = tempfile.SpooledTemporaryFile(
            max_size=NcSKOSDump.MAX_MEM,
            mode='w+',
            bufsize=-1,
            # suffix="",
            # prefix=template,
            # dir=None
        )

        # TODO: Work out whether we actually need to do this.
        # This might be overkill if we are only writing to stdout - we could
        # just print
        output_spool = tempfile.SpooledTemporaryFile(
            max_size=NcSKOSDump.MAX_MEM,
            mode='w+',
            bufsize=-1,
            # suffix="",
            # prefix=template,
            # dir=None
        )

        try:
            input_spool.write(subprocess.check_output(
                ncdump_command, shell=True, stderr=subprocess.STDOUT))
        except subprocess.CalledProcessError as e:
            logger.error(e.output)
            self._error = e.output
            exit(1)  # Don't proceed without ncdump output

        input_spool.seek(0)

        if xml_output:
            netcdf_tree = etree.fromstring(input_spool.read())
            input_spool.close()  # We don't need this any more

            namespace = '{' + netcdf_tree.nsmap[None] + '}'

            for skos_element \
                    in [attribute_element for attribute_element
                        in netcdf_tree.iterfind(path='.//' + namespace +
                                                'attribute')
                        if (attribute_element.attrib.get('name') ==
                            NcSKOSDump.SKOS_ATTRIBUTE)
                        ]:

                logger.debug('skos_element = %s', etree.tostring(
                    skos_element, pretty_print=False))
                uri = skos_element.attrib['value']
                logger.debug('uri = %s', uri)

                skos_lookup_dict = self.concept_fetcher.get_results(uri)
                logger.debug('skos_lookup_dict = %s', skos_lookup_dict)

                parent_element = skos_element.getparent()
                # Fix up formatting
                tail = parent_element[0].tail
                parent_element[-1].tail = tail

                # Write each key:value pair as a separate element
                for key, value in skos_lookup_dict.items():
                    new_element = parent_element.makeelement(
                        skos_element.tag, attrib={'name': key, 'value': value})
                    new_element.tail = tail
                    logger.debug('new_element = %s', etree.tostring(
                        new_element, pretty_print=False))
                    parent_element.append(new_element)

                # parent_element.remove(skos_element) # Delete original element

                output_spool.write(re.sub('(\r|\n)+', os.linesep,
                                          etree.tostring(netcdf_tree,
                                                         method='xml',
                                                         pretty_print=True,
                                                         xml_declaration=True,
                                                         encoding="UTF-8")))

        else:  # CDL output
            # TODO: Investigate potential issues around global attributes
            # Example: '    time:concept_uri =
            # "http://pid.geoscience.gov.au/def/voc/netCDF-ld-example-tos/time"
            # ;'
            attribute_regex_string = ('^\s*(\w*):' +
                                      NcSKOSDump.SKOS_ATTRIBUTE +
                                      '\s*=\s*"(http(s*)://.*)"\s*;\s*$')
            logger.debug('attribute_regex_string = %s', attribute_regex_string)
            attribute_regex = re.compile(attribute_regex_string)

            for input_line in input_spool.readlines():
                logger.debug('input_line = %s', input_line)

                output_spool.write(input_line)  # Output original line

                attribute_match = re.match(attribute_regex, input_line)
                if attribute_match is not None:
                    try:
                        logger.debug('attribute_match.groups() = %s',
                                     attribute_match.groups())
                        variable_name = attribute_match.group(1)
                        uri = attribute_match.group(2)
                        logger.debug('variable_name = %s, uri = %s',
                                     variable_name, uri)

                        skos_lookup_dict = self.concept_fetcher.get_results(
                            uri)
                        logger.debug('skos_lookup_dict = %s', skos_lookup_dict)

                        # Write each key:value pair as a separate line
                        for key, value in skos_lookup_dict.items():
                            modified_line = input_line.replace(variable_name +
                                                               ':' +
                                                               NcSKOSDump.SKOS_ATTRIBUTE,
                                                               variable_name + ':' + key
                                                               ).replace(uri, value)
                            logger.debug('modified_line = %s', modified_line)
                            output_spool.write(modified_line)

                        # continue  # Process next input line
                    except Exception as e:
                        logger.warning(
                            'URI resolution failed for %s: %s', uri, e.message)
                        self._error = e.message
                        # Fall back to original input line

            input_spool.close()

        output_spool.seek(0)  # Rewind output_spool ready for reading

        return output_spool

    def get_debug(self):
        return self._debug

    def set_debug(self, value):
        self._debug = value
        if self._debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

    debug = property(get_debug, set_debug, doc='Boolean debug output flag')

    def get_error(self):
        return self._error

    error = property(get_error, doc='Error message or None if no error')
