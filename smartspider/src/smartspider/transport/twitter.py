'''
Created on Dec 19, 2014

@author: Eloise
'''
from BeautifulSoup import BeautifulSoup,NavigableString
import logging
from smartspider.db.mongo_based import readSeedIndex,updateSeedIndex,storeCluster
from smartspider.analytics.named_entity_clustering import computeNamedEntityClusterAlgo1
import gzip
import StringIO
TWITTER = "twitter"
BR = mechanize.Browser()
BR.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0'),
('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
('Accept-Encoding' ,'gzip, deflate'),
('Accept-Language', 'en-US,en;q=0.5'),
('Cache-Control', 'max-age=0'),
('Connection', 'keep-alive')]

def fuzzyMatchName(fullName,aNER):
    return fullName.upper().replace(" ","") in aNER

def process_search_result(aResult,NER):
    resultEntries = aResult.findAll("div", {"class" : "account  js-actionable-user js-profile-popup-actionable " })
    meta_links = []
    for entry in resultEntries:
        fullName = entry.find("strong", {"class" : "fullname js-action-profile-name"}).getString()
        userName = entry.find("span", {"class" : "username js-action-profile-name" }).getString()
        try:
            if fuzzyMatchName(fullName,NER):
                meta_links.append(dict(fullName=fullName,userName=userName))
        except Exception as ex:
            print ex
    return meta_links

def constructSearchUrl(NER):
    return "%20OR%20".join([(x["firstName"]+" "+x["lastName"]).replace(" ","+") for x in NER])

def create_profiles_idx_from_twitter_search(namedEntityRecords,maxBatchSize=1):
    sizeOfRequest = len(namedEntityRecords)
    nerKeyList = [x['firstName'].upper().strip()+x['lastName'].upper().replace(" ","") for x in namedEntityRecords]
    allProfiles = []
    for a_batch in range(0,sizeOfRequest):
        try:
            sub_range = namedEntityRecords[a_batch:(a_batch+1)*maxBatchSize]
            url = "https://twitter.com/search?q=from%3A"+ \
            constructSearchUrl(sub_range)+\
            "&src=typd&mode=users"
            z=BR.open(url)
            logging.getLogger().log(logging.INFO,"url search for users: %s" % url)
            y=gzip.GzipFile(fileobj=StringIO.StringIO(buffer(z.get_data())),compresslevel=9)
            parsed = BeautifulSoup(y.read())
            matches = process_search_result(parsed,nerKeyList[a_batch:(a_batch+1)*maxBatchSize])
            if matches:
                updateSeedIndex("twitter_in",matches)
                logging.getLogger().log(logging.INFO,"matched users users: %s" % matches)
        except Exception as e:
            print sub_range
            print e

def process_twitter_profile(pBuckets):
    if not isinstance(pBuckets,list):
        pBuckets = [pBuckets]
    for a_profile in pBuckets:
        userName = a_profile['userName'][1:]
        z=BR.open("https://twitter.com/"+userName)
        logging.getLogger().log(logging.INFO,"processing usernameL %s" % userName)
        y=gzip.GzipFile(fileobj=StringIO.StringIO(buffer(z.get_data())),compresslevel=9)
        raw = y.read()
        parsed = BeautifulSoup(raw)
        profilesummary = parsed.find("p", {"class" : "ProfileHeaderCard-bio u-dir"},recursive=True).getString()
        if profilesummary:
            profilesummary = profilesummary.encode('ascii','ignore').decode('ascii')
        region = parsed.find("span", {"class" : "ProfileHeaderCard-locationText u-dir" }).getString() or "NONE"
        tweets = [x.getString() for x in parsed.findAll("p" ,{"class" : "ProfileTweet-text js-tweet-text u-dir"})]
        ner = dict(userName=userName,raw=raw,profilesummary=profilesummary,
                                    region=region,tweets=tweets,lastName=a_profile["fullName"].split(' ')[-1],firstName=" ".join(a_profile["fullName"].split(' ')[:-1]))
        cluster = computeNamedEntityClusterAlgo1(TWITTER,ner)
        try:
            storeCluster(TWITTER,cluster,ner)
        except Exception as ex:
            print cluster
            print ner
            print ex

def seed_twitter():
    while True:
        NER = readSeedIndex("linkedin")
        create_profiles_idx_from_twitter_search(NER)

def process_twitter():
    while True:
        entities = readSeedIndex("twitter_in")
        for aBucket in entities:
            process_twitter_profile(aBucket)
