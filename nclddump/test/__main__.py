'''
Main unit for test module
Unit tests for nclddump and ld_functions against a modified NetCDF file

Created on 7Oct.,2016

@author: Alex Ip
'''
import test_ld_functions
import test_nclddump

# Run all tests
print 'Testing ld_functions'
test_ld_functions.main()
print 'Testing nclddump'
test_nclddump.main()