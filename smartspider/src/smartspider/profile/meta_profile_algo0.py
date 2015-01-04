'''
Created on Jan 4, 2015

@author: Eloise
'''

from smartspider.db import LINKEDIN,TWITTER,MEETUP
from tornado.escape import xhtml_unescape
class MetaProfile(object):
    
    def __init__(self, profiles):        
        linkedin_profile = [x1 for x1 in profiles if LINKEDIN in x1['cluster']]
        linkedin_profile = linkedin_profile[0] if linkedin_profile else None
        twitter_profile = [x1 for x1 in profiles if TWITTER in x1['cluster']]
        twitter_profile = twitter_profile[0] if twitter_profile else None
        meetup_profile = [x1 for x1 in profiles if MEETUP in x1['cluster']]
        meetup_profile = meetup_profile[0] if meetup_profile else None
        self.name = linkedin_profile['entity']['firstName']+' '+linkedin_profile['entity']['lastName']        
        self.title = linkedin_profile['entity']['title']
        self.jobprofilesummary = linkedin_profile['entity']['profilesummary']
        self.work_interests = linkedin_profile['entity']['interests']
        
        if self.jobprofilesummary:
            self.jobprofilesummary = xhtml_unescape(self.jobprofilesummary)
        self.currentjob = linkedin_profile['entity']['current']
        self.currentjob = self.currentjob[0] if self.currentjob else None
        self.previous_jobs = linkedin_profile['entity']['previous'] or []
        self.education = linkedin_profile['entity']['education']
        self.region = linkedin_profile['entity']['region']
        if twitter_profile:
            self.interests_and_hobbies = twitter_profile['entity']['profilesummary']
            if self.interests_and_hobbies:
                self.interests_and_hobbies = xhtml_unescape(self.interests_and_hobbies)
            else:
                self.interests_and_hobbies = ""
            self.current_tweets = [xhtml_unescape(x) for x in twitter_profile['entity']['tweets'] if x]
        else:
            self.interests_and_hobbies = ""
            self.current_tweets = []
        if meetup_profile:
            org_groups = [xhtml_unescape(x[0]) for x in meetup_profile['entity']['groups'] if x[1] == 'Organizer']
            memb_groups = [xhtml_unescape(x[0]) for x in meetup_profile['entity']['groups'] if x[1] == 'Member']
            self.currentgroups = org_groups + memb_groups
        else:
            self.currentgroups = []
