'''
Created on Dec 21, 2014

@author: Steve Yalovitser

'''


from pymongo import Connection
from pymongo.database import Database



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

def retrieveClusters(source,clusters):
    db = MongoDBConnection.instance().get_connection().smartspider
    dbColl = db.raw_profiles    
    return dbColl.find({ "$or" : [ {"cluster" : x } for x in clusters]})


def findCluster(cluster,algo="algo0"):
    db = MongoDBConnection.instance().get_connection().smartspider
    dbColl = getattr(db,'cluster_'+algo)
    return dbColl.find_one({'meta_profile_key' : cluster.replace(' ','_')})
    
def retrieveProfilesFromCluster(cluster,algo="algo0"):
    aCluster = findCluster(cluster,algo)
    return retrieveClusters("NONE",aCluster['profiles'])


def updateSeedIndex(source,namedEntity):
    db = MongoDBConnection.instance().get_connection().smartspider
    if source not in db.collection_names():
        dbColl = db.create_collection(source,size=8*1024*1024*100,capped=True)
    else:
        dbColl = getattr(db,source)    
    for n in namedEntity:    
        dbColl.update({"cluster" : n}, {"cluster" : n} , upsert = True)
    

def readSeedIndex(source,tail=True):
    db = MongoDBConnection.instance().get_connection().smartspider
    dbColl = getattr(db,source)    
    if tail:
        return [x['cluster'] for x in dbColl.find(fields=["cluster"],tailable=True,await_data=True)]
    else:
        return [x['cluster'] for x in dbColl.find(fields=["cluster"])]

            
def searchCluster(searchterms,algo="algo0"):
    db = MongoDBConnection.instance().get_connection().smartspider        
    results = db.command("text","cluster_"+algo,search=searchterms)
    return [res['obj'] for res in results['results']]
    
        
    
    
    
    
    