'''
Created on Dec 19, 2014

@author: Eloise
'''
from BeautifulSoup import BeautifulSoup,NavigableString
from smartspider.analytics.named_entity_clustering import computeNamedEntityClusterAlgo1
from smartspider.db.mongo_based import storeCluster,updateSeedIndex,readSeedIndex
import mechanize
import gzip
import StringIO
import logging
LINKEDIN_INPUT = "linkedin_input"
LINKEDIN = "linkedin"
BR = mechanize.Browser()
BR.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0'),
('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
('Accept-Encoding' ,'gzip, deflate'),
('Accept-Language', 'en-US,en;q=0.5'),
('Cache-Control', 'max-age=0'),
('Connection', 'keep-alive')]
BR.set_handle_robots(False)


def process_linkedin_profile(a_link):
    # XXX DEAL WITH PARTIAL PROFILES
    logging.getLogger().log(logging.INFO,"processing link %s " % a_link)
    z=BR.open(a_link)
    y=gzip.GzipFile(fileobj=StringIO.StringIO(buffer(z.get_data())),compresslevel=9)
    raw = y.read()
    parsed = BeautifulSoup(raw)
    summary = parsed.find("div", {"class" : "profile-overview-content"},recursive=True)
    try:
        region = summary.find("span", {"class" : "locality"}).getString()
    except:
        region = None
    try:
        fullName = summary.find("span", {"class" : "full-name"}).getString().encode('ascii','ignore').decode('ascii')
    except:
        fullName = None
    lastName = fullName.split(' ')[-1]
    firstName = " ".join(fullName.split(' ')[:-1])
    try:
        title = summary.find("p", {"class" : "title"}).getString()
    except:
        title = None
    try:
        industry = summary.find("dd" , {"class" : "industry"}).getString()
    except:
        industry = None
    try:
        current = [x.getString() for x in summary.find("tr" , {"id" : "overview-summary-current"}).findChildren()[2:] if x.getString()]
    except:
        current = None
    try:
        previous = [x.getString() for x in summary.find("tr" , {"id" : "overview-summary-past"}).findChildren()[2:] if x.getString()]
    except:
        previous = None
    try:
        education = [x.getString() for x in summary.find("tr" , {"id" : "overview-summary-education"}).findChildren()[2:] if x.getString()]
    except:
        education = None
    try:
        profilesummary = parsed.find("p" , {"class" : "description"}).text
    except:
        profilesummary = None
    interests = [x.text for x in parsed.findAll("span" , {"class" : "endorse-item-name-text"})]
    ner = dict(raw=raw,link=a_link,region=region,title=title,
                              industry=industry,current=current,previous=previous,
                              education=education,profilesummary=profilesummary,interests=interests,
                              firstName=firstName,lastName=lastName)
    cluster = computeNamedEntityClusterAlgo1(LINKEDIN,ner)    
    storeCluster(LINKEDIN,cluster,ner)
    updateSeedIndex(LINKEDIN,[dict(firstName=firstName,lastName=lastName)])

def harvest_profiles_from_bing(constraint_based="'new+york+city'+and+'java'",max_links=5000):
    import string
    for s in string.letters:
        logging.getLogger().log(logging.INFO,"Seeding letter %s" %s)
        #url = "http://www.bing.com/search?q=site:https://www.linkedin.com/in+'/in/"+s+"'+"+constraint_based+"&qs=n&form=QBRE"
        a_url = "http://www.bing.com/search?q=site%3Ahttps%3A%2F%2Fwww.linkedin.com%2Fin+%27%2Fin%2F"+s+"%27+%27new+york+city%27+and+%27java%27&go=Submit&qs=bs&form=QBRE"
        logging.getLogger().log(logging.INFO,"url is %s" %a_url)
        z=BR.open(a_url)
        y=gzip.GzipFile(fileobj=StringIO.StringIO(buffer(z.get_data())),compresslevel=9)
        parsed = BeautifulSoup(y.read())
        results = parsed.findAll("li", {"class" : "b_algo"})
        linkedin_links = [x.find("a").get("href") for x in results]
        step = len(linkedin_links)
        repeating = False
        prev_links = None
        for page_offset in range(1,max_links,step):
            url =a_url+"&first="+str(page_offset)
            try:
                z=BR.open(url)
                logging.getLogger().log(logging.INFO,"url is %s" %url)
                y=gzip.GzipFile(fileobj=StringIO.StringIO(buffer(z.get_data())),compresslevel=9)
                parsed = BeautifulSoup(y.read())
                results = parsed.findAll("li", {"class" : "b_algo"})
                links_raw = [x.find("a").get("href") for x in results]
                [logging.log(logging.INFO,links_ele) for links_ele in links_raw]
                links_formatted = [x for x in links_raw if x.find("https://")>=0]
                repeating = prev_links == links_formatted
		if repeating:
		    break:
                prev_links = links_formatted
                updateSeedIndex(LINKEDIN_INPUT,links_formatted)    
            except Exception as ex:
                logging.getLogger().log(logging.CRITICAL,ex)
                logging.getLogger().log(logging.CRITICAL,url)
                

def main():
    while True:
        import time    
        links = readSeedIndex(LINKEDIN_INPUT)
        for link in links:
            try:
                process_linkedin_profile(link)
            except Exception as ex:
                print ex
                pass
