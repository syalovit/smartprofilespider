'''
Created on Dec 26, 2014

@author: Eloise
'''

from smartspider.transport.linkedin import clean_read as process_linkedin
from smartspider.util import set_logging_level_debug
def main():
    set_logging_level_debug()
    process_linkedin()

main()