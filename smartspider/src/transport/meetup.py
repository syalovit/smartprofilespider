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
BR = mechanize.Browser()
BR.set_handle_robots(False)
BR.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0'),
('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
('Accept-Encoding' ,'gzip, deflate'),
('Accept-Language', 'en-US,en;q=0.5'),
('Cache-Control', 'max-age=0'),
('Connection', 'keep-alive')]
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

       



 


