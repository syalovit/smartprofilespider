'''
Created on Dec 21, 2014

@author: Eloise
'''
import json
def storeCluster(source,cluster,entity):
    open("c:\\users\\eloise\\"+source+"_"+cluster,"w").write(json.dumps(entity))

def retrieveCluster(source,cluster):
    return open("c:\\users\\eloise\\"+source+"_"+cluster,"r").read()