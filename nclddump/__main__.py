'''
Created on 30 Sep 2016

@author: Alex Ip
'''
import sys
from nclddump import NCLDDump


def main():
    NCLDDump(sys.argv[1:])
    
if __name__ == '__main__':
    main()
