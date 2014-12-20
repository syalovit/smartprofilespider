'''
Created on Dec 19, 2014

@author: Eloise
'''
from BeautifulSoup import BeautifulSoup,NavigableString
import mechanize
import gzip
import StringIO
BR = mechanize.Browser()
BR.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0'),
('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
('Accept-Encoding' ,'gzip, deflate'),
('Accept-Language', 'en-US,en;q=0.5'),
('Cache-Control', 'max-age=0'),
('Connection', 'keep-alive')]
z=BR.open("https://www.linkedin.com/in/frankdgreco")
y=gzip.GzipFile(fileobj=StringIO.StringIO(buffer(z.get_data())),compresslevel=9)
parsed = BeautifulSoup(y.read())
summary = parsed.find("div", {"class" : "profile-overview-content"},recursive=True)
region = summary.find("span", {"class" : "locality"}).getString()
title = summary.find("p", {"class" : "title"}).getString()
industry = summary.find("dd" , {"class" : "industry"}).getString()
current = [x.getString() for x in summary.find("tr" , {"id" : "overview-summary-current"}).findChildren()[2:] if x.getString()]
previous = [x.getString() for x in summary.find("tr" , {"id" : "overview-summary-past"}).findChildren()[2:] if x.getString()]
education = [x.getString() for x in summary.find("tr" , {"id" : "overview-summary-education"}).findChildren()[2:] if x.getString()]
jobsummary = parsed.find("p" , {"class" : "description"}).text
skills = [x.text for x in parsed.findAll("span" , {"class" : "endorse-item-name-text"})]
