'''
Created on Dec 26, 2014

@author: Eloise
'''
from smartspider.transport.linkedin import harvest_profiles_from_bing 
from smartspider.util import set_logging_level_debug
def main():
    set_logging_level_debug()
    harvest_profiles_from_bing()
    
main()
