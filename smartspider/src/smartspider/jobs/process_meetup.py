'''
Created on Dec 26, 2014

@author: Eloise
'''

from smartspider.transport.meetup import main as process_meetup

def main():
    import logging
    logging.getLogger().setLevel(logging.INFO)    
    process_meetup()
    
main()