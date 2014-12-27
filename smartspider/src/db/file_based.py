'''
Created on Dec 21, 2014

@author: Eloise
'''
import json,os,sys
from collections import Counter
from itertools import combinations
import numpy as np
def storeCluster(source,cluster,entity):
    if not os.path.exists("c:\\users\\eloise\\spider\\"+os.path.dirname(cluster)):
        os.makedirs("c:\\users\\eloise\\spider\\"+os.path.dirname(cluster))
    f = open("c:\\users\\eloise\\spider\\"+cluster,"w")  
    json.dump(entity,f)
    f.close()

def retrieveCluster(source,cluster):
    return json.loads(open("c:\\users\\eloise\\spider\\"+cluster,"r").read())

def updateSeedIndex(source,namedEntity):
    f = open("c:\\users\\eloise\\spider\\"+source+"_index","a")
    str = json.dumps(namedEntity)
    f.write(str+"\n")  
    f.close()
        
def readSeedIndex(source):
    f = open("c:\\users\\eloise\\spider\\"+source+"_index","r")
    data = []
    for line in f.readlines(): 
        data.append(line)
    f.close()    
    return [json.loads(x) for x in list(set(data))]
    
def read_basic_cluster():
    entries = [x for x in os.listdir("c:\\users\\eloise\\spider\\") if x.find("_index") == -1]
    uniqueBuckets = list(set(["_".join(x.split("_")[:3]) for x in entries]))
    bucketMap = dict((x,[]) for x in uniqueBuckets)
    bucketProfileMap = {}
    for y in entries:
        key = "_".join(y.split("_")[:3])
        bucketMap[key].append(y)
    for k,v in bucketMap.iteritems():
        if len(v) >= 2:            
            try:
                bucketProfileMap[k] = [retrieveCluster('NONE',x)['profilesummary'] for x in v]
            except Exception as e:
                print e
    totalCount = [len(x) for x in bucketMap.values()]
    totalOnes = len([x for x in totalCount if x==1])
    totalTwos = len([x for x in totalCount if x==2])
    totalThrees = len([x for x in totalCount if x==3])
    totalOverThr = len([x for x in totalCount if x>3])
    bucketStats = dict(totalCount=len(totalCount),totalOnes=totalOnes,totalTwos=totalTwos,totalThrees=totalThrees,totalOverThr=totalOverThr)    
    return bucketMap,bucketProfileMap,bucketStats

def read_cluster_skills_algo1():
    entries = [x for x in os.listdir("c:\\users\\eloise\\spider\\") if x.find("_index") == -1]
    nameElements = [" ".join(x.split("_")[:2]) for x in entries]
    summaryElements = [x.split("_")[2:-1] for x in entries]
    allFeatures = np.array(sorted(set(sum(summaryElements,[]))))
    bucketMap = dict((x,{}) for x in list(set(nameElements)))
    for entry,nameEle,summEle in zip(entries,nameElements,summaryElements):
        pattern = np.array([0]*len(allFeatures))
        idxOfHit = [str((x == allFeatures).nonzero()[0][0]) for x in summEle]
        bucketMap[nameEle][entry] = set(idxOfHit) 
    reduxBucketMap = dict((x,[]) for x in nameElements)
    for a_key,a_value in bucketMap.iteritems():
        all_pattern_keys = a_value.keys()
        combos = combinations(a_value.keys(),2)
        for k1,k2 in combos:
            results = len(list(a_value[k1].intersection(a_value[k2])))
            reduxBucketMap[a_key].append([(k1,k2),results])
    return reduxBucketMap
                
            
        
        
    
    
    
    
    