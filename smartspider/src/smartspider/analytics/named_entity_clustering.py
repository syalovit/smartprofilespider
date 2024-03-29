'''
Created on Dec 21, 2014

@author: deductive systems
'''

WORKGRAPH = "workgraph"
PERSONALGRAPH = "personalgraph"

from collections import Counter
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import operator
import string
import logging
def normalizeRegion(source,region):
    firstPass = region.upper().replace("GREATER","").replace("CITY","").replace(" ","")[:4]
    return "NEWY" if region.upper().find("NY") >=0 or region.upper().find("NEW YORK") >= 0 or region.upper().find("NEWYORK") >= 0 else firstPass

def normalizeWords(text_list):
    port = PorterStemmer()    
    replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))    
    return [port.stem(str(x.encode('ascii','ignore').decode('ascii')).upper().translate(replace_punctuation)) for x in text_list if x.isalpha() and x not in stopwords.words('english')]
    
    
def classifyProfile(source,ner):
    if source == 'linkedin':
        return WORKGRAPH
    else:
        return PERSONALGRAPH

def normalizeInterestWords(source,ner):

    if source == "linkedin":
        words = ner['interests'] + ner['profilesummary'].split(' ')
    else:
        profilesummary = ner['profilesummary'].split(' ')
    if profilesummary:
        return normalizeWords(profilesummary)
    else:
        return []


def normalizeSummary(source,ner):
    # We use interests from linkedin which is a better match to twitter and meetup
    # we will create a singleton stemmer later
    port = PorterStemmer()

    try:
        if ner['profilesummary']:
            ele = normalizeWords(ner['profilesummary'].split(" "))
            hiScore = [x[0] for x in list(Counter(ele).most_common(10))]        
            return "_".join(hiScore)
        else:
            return "NONE"
    except Exception as ex:
        logging.getLogger().log(logging.CRITICAL,"Failed summarizing %s with error %s" % (ner, ex))

        return "NONE"

def normalizeName(source,name):
    return name.upper().replace("/","").encode('ascii','ignore')

def computeNamedEntityClusterAlgo1(source,ner):    
    return normalizeName(source,ner["lastName"])  +"_"+normalizeName(source,ner["firstName"])+"_"+normalizeRegion(source,ner["region"])+"_"+normalizeSummary(source,ner)+"_"+source

def computeNamedEntityClusterBucketAlgo1(source,ner):
    return normalizeName(source,ner["lastName"])  +"_"+normalizeName(source,ner["firstName"])+"_"+normalizeRegion(source,ner["region"])

def genGraph(profiles,limit=6):
    graphtags = reduce(operator.add,[Counter(a_counter.iteritems()) for a_counter in profiles], Counter())
    return sorted(graphtags,key=graphtags.get,reverse=True)[:limit]
    
def genWorkGraph(cluster_record,algo="algo0"):
    return genGraph(cluster_record.get(WORKGRAPH,[{}]))

def genPersonalGraph(cluster_record,algo="algo0"):
    return genGraph(cluster_record.get(PERSONALGRAPH,[{}]))
    