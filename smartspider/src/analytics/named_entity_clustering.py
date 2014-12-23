'''
Created on Dec 21, 2014

@author: Eloise
'''

from metaphone import doublemetaphone
def normalizeRegion(source,region):
    return region.upper().replace("GREATER","").replace("CITY","").replace(" ","")[:4]
    

def normalizeSummary(source,profilesummary):
    if profilesummary:
        elements = [x for x in sorted(profilesummary.split(" ")) if x.isalpha()]
        return "".join(["".join(list(doublemetaphone(x))) for x in elements])[:20]
    else:
        return "NONE"

def normalizeName(source,name):
    return name.upper().replace("/","")

def computeNamedEntityClusterAlgo1(source,ner):    
    return normalizeName(source,ner["lastName"])  +"_"+normalizeName(source,ner["firstName"])+"_"+normalizeRegion(source,ner["region"])+"_"+normalizeSummary(source,ner["profilesummary"])+"_"+source