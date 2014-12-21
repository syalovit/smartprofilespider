'''
Created on Dec 19, 2014

@author: Eloise
'''
from BeautifulSoup import BeautifulSoup,NavigableString
import mechanize
from db.file_based import readSeedIndex
import gzip
import StringIO
BR = mechanize.Browser()
BR.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0'),
('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
('Accept-Encoding' ,'gzip, deflate'),
('Accept-Language', 'en-US,en;q=0.5'),
('Cache-Control', 'max-age=0'),
('Connection', 'keep-alive')]

def process_search_result(aResult):
    pass

def constructSearchUrl(listOfNames):
    return "%20OR%20".join(listOfNames)

def harvest_profiles_from_twitter_search(namedEntityRecords,maxBatchSize=20):
    sizeOfRequest = len(namedEntityRecords)
    allProfiles = []
    for a_batch in range(0,sizeOfRequest):
        url = "https://twitter.com/search?q=from%3A"+ \
        namedEntityRecords[a_batch:(a_batch+1)*maxBatchSize]+\
        "&src=typd&mode=users"
        z=BR.open(url)
        y=gzip.GzipFile(fileobj=StringIO.StringIO(buffer(z.get_data())),compresslevel=9)
        parsed = BeautifulSoup(y.read())
        allProfiles = allProfiles + process_search_result(parsed)

def main():
    idx = readSeedIndex("linkedin")
    NER = [x['lastName'] for x in idx]
    print harvest_profiles_from_twitter_search(NER)
#z=BR.open("https://twitter.com/frankgreco")
#
#'''https://twitter.com/search?q=from%3Agreco&src=typd&mode=users'''
#y=gzip.GzipFile(fileobj=StringIO.StringIO(buffer(z.get_data())),compresslevel=9)
#parsed = BeautifulSoup(y.read())
#profilesummary = parsed.find("p", {"class" : "ProfileHeaderCard-bio u-dir"},recursive=True).getString()
#region = parsed.find("span", {"class" : "ProfileHeaderCard-locationText u-dir" }).getString()
#tweets = [x.getString() for x in parsed.findAll("p" ,{"class" : "ProfileTweet-text js-tweet-text u-dir"})]
main()