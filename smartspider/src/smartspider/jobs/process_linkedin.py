'''
Created on Dec 26, 2014

@author: Eloise
'''

from smartspider.transport.linkedin import main as process_linkedin

def main():
    import logging
    logging.getLogger().setLevel(logging.INFO)
    process_linkedin()

main()