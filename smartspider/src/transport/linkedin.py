'''
Created on Dec 19, 2014

@author: Eloise
'''
from BeautifulSoup import BeautifulSoup,NavigableString
from analytics.named_entity_clustering import computeNamedEntityClusterAlgo1
from db.file_based import storeCluster
import mechanize
import gzip
import StringIO
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
    print a_link
    z=BR.open(a_link)
    y=gzip.GzipFile(fileobj=StringIO.StringIO(buffer(z.get_data())),compresslevel=9)
    raw = y.read()
    parsed = BeautifulSoup(raw)
    summary = parsed.find("div", {"class" : "profile-overview-content"},recursive=True)
    region = summary.find("span", {"class" : "locality"}).getString()
    fullName = summary.find("span", {"class" : "full-name"}).getString()
    lastName = fullName.split(' ')[-1]
    firstName = " ".join(fullName.split(' ')[:-1])
    title = summary.find("p", {"class" : "title"}).getString()
    industry = summary.find("dd" , {"class" : "industry"}).getString()
    current = [x.getString() for x in summary.find("tr" , {"id" : "overview-summary-current"}).findChildren()[2:] if x.getString()]
    previous = [x.getString() for x in summary.find("tr" , {"id" : "overview-summary-past"}).findChildren()[2:] if x.getString()]
    education = [x.getString() for x in summary.find("tr" , {"id" : "overview-summary-education"}).findChildren()[2:] if x.getString()]
    jobsummary = parsed.find("p" , {"class" : "description"}).text
    interests = [x.text for x in parsed.findAll("span" , {"class" : "endorse-item-name-text"})]
    cluster = computeNamedEntityClusterAlgo1(LINKEDIN,lastName, firstName)    
    storeCluster(LINKEDIN,cluster,dict(raw=raw,link=a_link,region=region,title=title,
                              industry=industry,current=current,previous=previous,
                              education=education,jobsummary=jobsummary,interests=interests,
                              firstName=firstName,lastName=lastName))

def harvest_profiles_from_bing(constraint_based="new+york+city+tech+java",max_links=5000):
    z=BR.open("http://www.bing.com/search?q=site:https://www.linkedin.com/in+"+constraint_based+"&qs=n&form=QBRE")
    y=gzip.GzipFile(fileobj=StringIO.StringIO(buffer(z.get_data())),compresslevel=9)
    parsed = BeautifulSoup(y.read())
    results = parsed.findAll("li", {"class" : "b_algo"})
    linkedin_links = [x.find("a").get("href") for x in results]
    step = len(linkedin_links)
    for page_offset in range(1,max_links,step):
        z=BR.open("http://www.bing.com/search?q=site:https://www.linkedin.com/in+new+york+city+tech+java&qs=n&form=QBRE&first="+str(page_offset))
        y=gzip.GzipFile(fileobj=StringIO.StringIO(buffer(z.get_data())),compresslevel=9)
        parsed = BeautifulSoup(y.read())
        results = parsed.findAll("li", {"class" : "b_algo"})
        links = [x.find("a").get("href") for x in results]
        linkedin_links = linkedin_links + links
        
    return linkedin_links    
    

def main():
    links = harvest_profiles_from_bing(max_links=20)
    for link in links:
        try:
            process_linkedin_profile(link)
        except:
            pass
     
main()