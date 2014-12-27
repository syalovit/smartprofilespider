from smartspider.db.mongo_based import  read_basic_cluster,read_cluster_skills_algo1

def main():
    import pprint
    
    #pprint.pprint(read_cluster_skills_algo1())
    bucketMap,bucketProfileMap,bucketStats = read_basic_cluster()
#    import pprint
    pprint.pprint(bucketProfileMap)
    print bucketStats
    
main()
