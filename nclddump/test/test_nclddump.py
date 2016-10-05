'''
Quick-and-dirty test of nclddump on a modified NetCDF file

Created on 4Oct.,2016

@author: Alex Ip
'''
from nclddump import NCLDDump

def main():
    nc_path = 'sst.ltm.1971-2000_skos.nc'
    
    nclddump_object = NCLDDump(['-h', nc_path, '--skos', 'lang=pl', 'altLabels=True', 'narrower=True', 'broader=True'], debug=True)
    
    if nclddump_object.error:
        print 'nclddump error = "%s"' % nclddump_object.error   

if __name__ == '__main__':
    main()