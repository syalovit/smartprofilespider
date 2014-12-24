'''
Created on Dec 19, 2014

@author: Eloise
'''

'''
Created on Dec 19, 2014

@author: Eloise
'''
from BeautifulSoup import BeautifulSoup,NavigableString
import mechanize
import gzip
import StringIO
import re
from db.file_based import readSeedIndex,updateSeedIndex,storeCluster
from analytics.named_entity_clustering import computeNamedEntityClusterAlgo1

BR = mechanize.Browser()
BR.set_handle_robots(False)
BR.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0'),
('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
('Accept-Encoding' ,'gzip, deflate'),
('Accept-Language', 'en-US,en;q=0.5'),
('Cache-Control', 'max-age=0'),
('Connection', 'keep-alive')]
MEETUP = "meetup"
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
#    return "http://www.bing.com/search?q=meetup+member+"+(NER["firstName"]+" "+NER["lastName"]).replace(" ","+")+"&qs=n&form=QBRE&pq=meetup+member+"+(NER["firstName"]+" "+NER["lastName"]).replace(" ","+") 
    return "http://www.bing.com/search?q=meetup+member+"+(NER["firstName"]+" "+NER["lastName"]).replace(" ","+") 


def create_profiles_idx_from_meetup_search(namedEntityRecord):
    name = namedEntityRecord['firstName']+" "+namedEntityRecord['lastName']
    def process_name(x):
        return x.text.split('-')[0]    
    def fuzzy_match(x,name):
        return x.upper() == name.upper() or name.upper().find(x.upper().replace('.','')) >= 0
            
    try:
        url = constructSearchUrl(namedEntityRecord)
        print url
        z=BR.open(url)
        y=gzip.GzipFile(fileobj=StringIO.StringIO(buffer(z.get_data())),compresslevel=9)
        parsed = BeautifulSoup(y.read())
        results = parsed.findAll("li", {"class" : "b_algo"})
        links = [x.find("a") for x in results]
        meta_links = []
        for x in results:
            data = x.find("a")
            a_name = process_name(data)
            link = data.get('href')
            if link.find('member') > -1 and link.find("meetup.com") > -1 and fuzzy_match(a_name,name):
                meta_links.append((name,link))
        ##### ABOVE WE ACQUIRED MEETUP GROUPS #### NOW WE JUST USE ONE OF THE GROUPS TO TRAVERSE THE MEETUP GRAPH
        if meta_links:
            the_target_group = meta_links[0][1]
            print the_target_group
            z=BR.open(the_target_group+"?showAllGroups=true#my-meetup-groups-list") 
            y=gzip.GzipFile(fileobj=StringIO.StringIO(buffer(z.get_data())),compresslevel=9)
            parsed = BeautifulSoup(y.read())
            region=parsed.find("p" , {"itemprop":"address"})
            userName=parsed.find("div" , { "id" : re.compile("member_") })
            if userName:
                userName = userName.attrs[0][1].split("_")[1]
            else:
                userName = 'NONE'
            # replace this with nlp processing for location
            def process_location(x):
                return x[0].split(',')[0],x[2],x[3],x[4]
            ele = [x.text for x in region.findAll()]
            location = process_location(ele)
            interests = " ".join([x.text for x in parsed.findAll("a" , {"class" : re.compile("topic-id-")})])
            group_raw=parsed.findAll("li" , {"class" : re.compile("groupinfo-widget")})
            group_details = []
            def extract_group_details(x):
                return x.find("div" , {"class" : "D_name" }), x.find("div" , {"class" : "member-role" })
            
            for x in group_raw:
                grp_name,member_role = extract_group_details(x)
                if grp_name is not None and member_role is not None:
                    group_details.append([grp_name.text,member_role.text])
    
            ner = dict(userName=userName,profilesummary=interests,
                                        region=" ".join(list(location)),groups=group_details,lastName=namedEntityRecord['lastName'],firstName=namedEntityRecord['firstName'])
            cluster = computeNamedEntityClusterAlgo1(MEETUP,ner)
            try:
                storeCluster(MEETUP,cluster,ner)
            except Exception as ex:
                print cluster
                print namedEntityRecord
                print ex
            
    
    except Exception as e:
        print namedEntityRecord
        print e
    
    
    
    
    
    
    
    

def main():
    NER = readSeedIndex("linkedin")
    for a_ner in NER:
        create_profiles_idx_from_meetup_search(a_ner)

main()
       



 

