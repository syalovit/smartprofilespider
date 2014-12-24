'''
Created on Dec 21, 2014

@author: Eloise
'''
import json,os,sys
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
    return bucketMap

    
        
    
    
    
    
    