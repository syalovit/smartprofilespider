'''
Created on Dec 21, 2014

@author: Steve Yalovitser

'''
import json,os,sys
from collections import Counter
from itertools import combinations
import numpy as np
from smartspider.analytics.named_entity_clustering import countText
from pymongo import Connection
from pymongo.database import Database
from pymongo import TEXT

DBNAME = "localhost"
USERNAME = "talneuro"
PASSWD = "talneuro"

class MongoDBConnection:
    
    _instance = None
    
    def __init__(self):
        self.connection = Connection(DBNAME,tz_aware=True)
        self.admin_db = Database(self.connection,"admin")
        self.admin_db.authenticate(USERNAME,PASSWD)
    
    @classmethod 
    def instance(cls):
        if cls._instance == None:
            MongoDBConnection._instance = MongoDBConnection()
        return MongoDBConnection._instance

    def reauthenticate(self):
        self.admin_db = Database(self.connection,"admin")
        self.admin_db.authenticate(USERNAME,PASSWD)

    
    def reconnect(self):
        self.connection = Connection(DBNAME)
        self.reauthenticate()

        
    def get_connection(self):
        return self.connection
    

# brute force mechanism, will need to be writting into buckets ahead of time for it to scale
def storeCluster(source,cluster,entity):
    db = MongoDBConnection.instance().get_connection().smartspider
    dbColl = db.raw_profiles    
    dbColl.update({"cluster" : cluster} ,  {"cluster" : cluster, "entity" : entity}, upsert = True)

def retrieveCluster(source,cluster):
    db = MongoDBConnection.instance().get_connection().smartspider
    dbColl = db.raw_profiles    
    return dbColl.find_one({"cluster" : cluster})


def updateSeedIndex(source,namedEntity):
    db = MongoDBConnection.instance().get_connection().smartspider
    if source not in db.collection_names():
        dbColl = db.create_collection(source,size=8*1024*1024*100,capped=True)
    else:
        dbColl = getattr(db,source)    
    for n in namedEntity:    
        dbColl.update({"cluster" : n}, {"cluster" : n} , upsert = True)
    

def readSeedIndex(source):
    db = MongoDBConnection.instance().get_connection().smartspider
    dbColl = getattr(db,source)    
    return [x['cluster'] for x in dbColl.find(fields=["cluster"],tailable=True,await_data=True)]

def create_basic_cluster_algo0():
    db = MongoDBConnection.instance().get_connection().smartspider
    raw_profiles = db.raw_profiles
    cluster_algo0 = db.cluster_algo0
    cluster_algo0.drop()
    cluster_algo0.create_index([('features' , TEXT)], default_language='english')
    all_clusters = [x["cluster"] for x in raw_profiles.find(fields=["cluster"])]
    tags = []
    for y in all_clusters:
        key = "_".join(y.split("_")[:3])
        if y.find("linkedin") >= 0:
            cluster_algo0.update({"meta_profile_key" : key } , {"meta_profile_key" : key , "features" : y.replace("_"," ") }, upsert = True)
            
        cluster_algo0.update({"meta_profile_key" : key } , {"$addToSet" : { "profiles" : y } }, upsert = True)
        new_tags = [x for x in y.replace('.','').split("_")[3:-1] if x!="NONE"]        
        tags = tags + new_tags 
    counter = countText(tags)
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
    for k,v in bucketMap.iteritems():
        if len(v) >= 2:            
            try:
                bucketProfileMap[k] = [retrieveCluster('NONE',v)['entity']['profilesummary'] for v in v]
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
                
            
        
        
    
    
    
    
    