'''
Created on Dec 26, 2014

@author: Eloise
'''
from smartspider.transport.linkedin import harvest_profiles_from_bing 

def main():
    harvest_profiles_from_bing(max_links=10000)
    
main()
import smartspider.jobs.process_linkedin
import smartspider.jobs.process_twitter
import smartspider.jobs.process_meetup