'''
Created on Dec 26, 2014

@author: deductive systems
'''

from smartspider.transport.meetup import main as process_meetup
from smartspider.util import set_logging_level_debug
def main():
    set_logging_level_debug() 
    process_meetup()
    
main()