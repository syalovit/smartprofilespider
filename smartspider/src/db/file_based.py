'''
Created on Dec 21, 2014

@author: Eloise
'''
import json,os,sys
from collections import Counter
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
    for y in entries:
        bucketMap["_".join(y.split("_")[:3])].append(y)
    
    totalCount = [len(x) for x in bucketMap.values()]
    totalOnes = len([x for x in totalCount if x==1])
    totalTwos = len([x for x in totalCount if x==2])
    totalThrees = len([x for x in totalCount if x==3])
    totalOverThr = len([x for x in totalCount if x>3])
    bucketStats = dict(totalCount=len(totalCount),totalOnes=totalOnes,totalTwos=totalTwos,totalThrees=totalThrees,totalOverThr=totalOverThr)
    return bucketMap,entries,bucketStats

def read_cluster_skills_algo1():
    entries = [x for x in os.listdir("c:\\users\\eloise\\spider\\") if x.find("_index") == -1]
    nameElements = [" ".join(x.split("_")[:2]) for x in entries]
    summaryElements = [x.split("_")[3:-1] for x in entries]
    allFeatures = np.array(sorted(set(sum(summaryElements,[]))))
    bucketMap = dict((x,{}) for x in list(set(nameElements)))
    for entry,nameEle,summEle in zip(entries,nameElements,summaryElements):
        pattern = np.array([0]*len(allFeatures))
        idxOfHit = [str((x == allFeatures).nonzero()[0][0]) for x in summEle]
        bucketMap[nameEle]["-".join(idxOfHit)] = entry 
    reduxBucketMap = {}
    for a_key,a_value in bucketMap.iteritems():
        all_pattern_keys = a_value.keys()
        summaryBuckets = {}
        for a_key,a_value in a_value.iteritems():
            bucketKeys = a_key.split("-")
            for bucketKey in bucketKeys:
                the_list = summaryBuckets.get(bucketKey,[])
                the_list.append(a_value)
                summaryBuckets[bucketKey] = the_list
        reduxBucketMap[a_key] = summaryBuckets
    return reduxBucketMap
                
            
        
        
    
    
    
    
    