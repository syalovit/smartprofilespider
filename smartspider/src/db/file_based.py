'''
Created on Dec 21, 2014

@author: Eloise
'''
import json
def storeCluster(source,cluster,entity):    
    f = open("c:\\users\\eloise\\"+source+"_"+cluster,"w")  
    json.dump(entity,f)
    f.close()

def retrieveCluster(source,cluster):
    return json.loads(open("c:\\users\\eloise\\"+source+"_"+cluster,"r").read())

def updateSeedIndex(source,namedEntity):
    f = open("c:\\users\\eloise\\"+source+"_index","a")
    str = json.dumps(namedEntity)
    f.write(str+"\n")  
    f.close()
        
def readSeedIndex(source):
    f = open("c:\\users\\eloise\\"+source+"_index","r")
    data = []
    for line in f.readlines(): 
        data.append(json.loads(line))
    f.close()
    return data
    return data
    