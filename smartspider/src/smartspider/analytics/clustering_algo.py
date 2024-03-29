'''
Created on Jan 4, 2015

@author: deductive systems
'''
from smartspider.db.mongo_based import MongoDBConnection
from smartspider.analytics.named_entity_clustering import normalizeWords,normalizeInterestWords,classifyProfile
from pymongo import TEXT
import os
from collections import Counter
from itertools import combinations
import numpy as np

def create_basic_cluster_algo0():
    from smartspider.transport.linkedin import LINKEDIN
    db = MongoDBConnection.instance().get_connection().smartspider
    raw_profiles = db.raw_profiles
    cluster_algo0 = db.cluster_algo0
    cluster_algo0.drop()
    cluster_algo0.create_index([('features' , TEXT)], default_language='english')
#    all_clusters = [x["cluster"] for x in raw_profiles.find(fields=["cluster"])]
    tags = []
    for y in raw_profiles.find():
        cluster_key = y['cluster']
        key_elements = cluster_key.split("_")
        key = "_".join(key_elements[:3])
        cluster_data = y['entity'] 
        profilesummary = cluster_data.get('profilesummary','') or ''               
        if cluster_key.find(LINKEDIN) >= 0:
            region = cluster_data.get('region','') or ''            
            profile_data =  profilesummary + region 
            cluster_algo0.update({"meta_profile_key" : key } , {"meta_profile_key" : key , 
                                                                "features" : profile_data }, upsert = True)
            new_tags = profile_data.split(' ')            
        else:
            new_tags = profilesummary.split(' ')
        
        source = key_elements[-1]  
                      
        tags = tags + new_tags
        graph = Counter(normalizeWords(new_tags))  
        class_of_graph = classifyProfile(source,cluster_data)           
        cluster_algo0.update({"meta_profile_key" : key } , {"$addToSet" : { "profiles" : cluster_key , class_of_graph : graph } }, upsert = True)
    counter = Counter(normalizeWords(tags))
    db.meta_features.update({"algo": "cluster_algo0"} , {"algo": "cluster_algo0", "features" : counter }, upsert=True)
    
def read_basic_cluster():
    db = MongoDBConnection.instance().get_connection().smartspider
    from smartspider.transport.twitter import TWITTER
    from smartspider.transport.meetup import MEETUP
    from smartspider.transport.linkedin import LINKEDIN
    raw_profiles = db.raw_profiles
    all_clusters = [x["cluster"] for x in raw_profiles.find(fields=["cluster"])]
    uniqueBuckets = list(set(["_".join(x.split("_")[:3]) for x in all_clusters]))
    bucketMap = dict((x,[]) for x in uniqueBuckets)
    bucketProfileMap = {}
    for y in all_clusters:
        key = "_".join(y.split("_")[:3])
        bucketMap[key].append(y)
#    for k,v in bucketMap.iteritems():
#        if len(v) >= 2:            
#            try:
#                bucketProfileMap[k] = [retrieveCluster('NONE',v)['entity']['profilesummary'] for v in v]
#            except Exception as e:
#                print e
    totalCount = [len(x) for x in bucketMap.values()]
    totalOnes = len([x for x in totalCount if x==1])
    totalTwos = len([x for x in totalCount if x==2])
    totalThrees = len([x for x in totalCount if x==3])
    totalOverThr = len([x for x in totalCount if x>3])
    bucketStats = dict(totalCount=len(totalCount),totalOnes=totalOnes,totalTwos=totalTwos,totalThrees=totalThrees,totalOverThr=totalOverThr)    
    return bucketMap,bucketProfileMap,bucketStats
#
#def read_cluster_skills_algo1():
#    entries = [x for x in os.listdir("c:\\users\\deductive systems\\spider\\") if x.find("_index") == -1]
#    nameElements = [" ".join(x.split("_")[:2]) for x in entries]
#    summaryElements = [x.split("_")[2:-1] for x in entries]
#    allFeatures = np.array(sorted(set(sum(summaryElements,[]))))
#    bucketMap = dict((x,{}) for x in list(set(nameElements)))
#    for entry,nameEle,summEle in zip(entries,nameElements,summaryElements):
#        pattern = np.array([0]*len(allFeatures))
#        idxOfHit = [str((x == allFeatures).nonzero()[0][0]) for x in summEle]
#        bucketMap[nameEle][entry] = set(idxOfHit) 
#    reduxBucketMap = dict((x,[]) for x in nameElements)
#    for a_key,a_value in bucketMap.iteritems():
#        all_pattern_keys = a_value.keys()
#        combos = combinations(a_value.keys(),2)
#        for k1,k2 in combos:
#            results = len(list(a_value[k1].intersection(a_value[k2])))
#            reduxBucketMap[a_key].append([(k1,k2),results])
#    return reduxBucketMap
                