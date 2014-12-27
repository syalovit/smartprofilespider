'''
Created on Dec 21, 2014

@author: Eloise
'''

from metaphone import doublemetaphone
from collections import Counter


def normalizeRegion(source,region):
    firstPass = region.upper().replace("GREATER","").replace("CITY","").replace(" ","")[:4]
    return "NEWY" if region.upper().find("NY") >=0 or region.upper().find("NEW YORK") >= 0 or region.upper().find("NEWYORK") >= 0 else firstPass
    


def normalizeSummary(source,ner):
    # We use interests from linkedin which is a better match to twitter and meetup
    # we will create a singleton stemmer later
    from nltk.stem import PorterStemmer
    from nltk.corpus import stopwords
    import string
    port = PorterStemmer()

    if source == "linked":
        profilesummary = ner['interests'] or ner['profilesummary']
    else:
        profilesummary = ner['profilesummary']
    if profilesummary:
        elements = [x.upper() for x in sorted(profilesummary.split(" ")) if x.isalpha() and x not in string.punctuation and x not in stopwords.words('english')]
        ele = [port.stem(x) for x in elements]
        hiScore = [x[0] for x in list(Counter(ele).most_common(10))]        
        return "_".join(hiScore)
    else:
        return "NONE"

def normalizeName(source,name):
    return name.upper().replace("/","").encode('ascii','ignore')

def computeNamedEntityClusterAlgo1(source,ner):    
    return normalizeName(source,ner["lastName"])  +"_"+normalizeName(source,ner["firstName"])+"_"+normalizeRegion(source,ner["region"])+"_"+normalizeSummary(source,ner)+"_"+source

def computeNamedEntityClusterBucketAlgo1(source,ner):
    return normalizeName(source,ner["lastName"])  +"_"+normalizeName(source,ner["firstName"])+"_"+normalizeRegion(source,ner["region"])