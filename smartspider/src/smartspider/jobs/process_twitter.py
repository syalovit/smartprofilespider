'''
Created on Dec 26, 2014

@author: Eloise
'''

from smartspider.transport.twitter import process_twitter_clean as process_twitter
from smartspider.util import set_logging_level_debug
def main():
    set_logging_level_debug()
    process_twitter("@lukatomasevic")
    
main()