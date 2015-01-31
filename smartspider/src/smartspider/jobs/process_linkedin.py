'''
Created on Dec 26, 2014

@author: deductive systems
'''

from smartspider.transport.linkedin import process_google_api_profiles as process_linkedin
from smartspider.util import set_logging_level_debug
def main():
    set_logging_level_debug()
    process_linkedin()

main()