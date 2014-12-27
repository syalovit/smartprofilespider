'''
Created on Dec 26, 2014

@author: Eloise
'''

from smartspider.transport.twitter import main as process_twitter

def main():
    import logging
    logging.getLogger().setLevel(logging.INFO)
    process_twitter()
    
main()