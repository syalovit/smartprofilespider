'''
Created on Dec 21, 2014

@author: Eloise
'''
import json,os
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
        data.append(json.loads(line))
    f.close()
    return data
    return data
    