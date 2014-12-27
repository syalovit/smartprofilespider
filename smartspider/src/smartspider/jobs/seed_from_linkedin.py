'''
Created on Dec 26, 2014

@author: Eloise
'''
from smartspider.transport.linkedin import harvest_profiles_from_bing 

def main():
    import logging
    logging.getLogger().setLevel(logging.INFO)    
    harvest_profiles_from_bing(max_links=1000000)
    
main()
