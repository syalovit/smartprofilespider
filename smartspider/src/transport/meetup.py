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
BR = mechanize.Browser()
BR.set_handle_robots(False)
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
            y=gzip.GzipFile(fileobj=StringIO.StringIO(buffer(z.get_data())),compresslevel=9)
            parsed = BeautifulSoup(y.read())
            matches = process_search_result(parsed,nerKeyList[a_batch:(a_batch+1)*maxBatchSize])
            if matches:
                updateSeedIndex("twitter_in",matches)
        except Exception as e:
            print url
            print e





name = 'frank greco'
z=BR.open("http://www.bing.com/search?q=meetup+member+frank+greco&qs=n&form=QBRE&pq=meetup+member+frank+greco")
y=gzip.GzipFile(fileobj=StringIO.StringIO(buffer(z.get_data())),compresslevel=9)
parsed = BeautifulSoup(y.read())
results = parsed.findAll("li", {"class" : "b_algo"})

def process_name(x):
    return x.text.split('-')[0]

def fuzzy_match(x):
    return x.upper() == name.upper()

links = [x.find("a") for x in results]
meta_links = []
for x in results:
    data = x.find("a")
    a_name = process_name(data)
    link = data.get('href')
    if fuzzy_match(a_name) and link.find('member') > -1:
        meta_links.append((name,link))

##### ABOVE WE ACQUIRED MEETUP GROUPS #### NOW WE JUST USE ONE OF THE GROUPS TO TRAVERSE THE MEETUP GRAPH
the_target_group = meta_links[0][1]
z=BR.open(the_target_group+"?showAllGroups=true#my-meetup-groups-list") 
y=gzip.GzipFile(fileobj=StringIO.StringIO(buffer(z.get_data())),compresslevel=9)
parsed = BeautifulSoup(y.read())
region=parsed.find("p" , {"itemprop":"address"})

# replace this with nlp processing for location
def process_location(x):
    return x[0].split(',')[0],x[2],x[3],x[4]
ele = [x.text for x in region.findAll()]
location = process_location(ele)
interests = [x.text for x in parsed.findAll("a" , {"class" : re.compile("topic-id-")})]
group_raw=parsed.findAll("li" , {"class" : re.compile("groupinfo-widget")})
group_details = []
def extract_group_details(x):
    return x.find("div" , {"class" : "D_name" }), x.find("div" , {"class" : "member-role" })

for x in group_raw:
    grp_name,member_role = extract_group_details(x)
    if grp_name is not None and member_role is not None:
        group_details.append([grp_name.text,member_role.text])

def main():
    NER = readSeedIndex("linkedin")
    create_profiles_idx_from_meetup_search(NER)
    entities = readSeedIndex("twitter_in")
    for aBucket in entities:
        process_twitter_profile(aBucket)
main()
       



 


