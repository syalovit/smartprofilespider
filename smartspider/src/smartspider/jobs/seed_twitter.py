'''
Created on Dec 26, 2014

@author: deductive systems
'''
from smartspider.transport.twitter import seed_twitter 
from smartspider.util import set_logging_level_debug
def main():
    set_logging_level_debug()
    seed_twitter()
    
main()
