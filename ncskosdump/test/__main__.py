"""
Main unit for test module
Unit tests for ncskosdump and ld_functions against a modified NetCDF file

Created on 7Oct.,2016

@author: Alex Ip
"""
import test_ld_functions
import test_ncskosdump

# Run all tests
print '* Testing ld_functions module:'
test_ld_functions.main()
print '* Testing ncskosdump module:'
test_ncskosdump.main()
