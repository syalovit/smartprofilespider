from db.file_based import  read_basic_cluster,read_cluster_skills_algo1

def main():
    import pprint
    
    pprint.pprint(read_cluster_skills_algo1())
#    bucketMap,bucketStats = read_basic_cluster()
#    import pprint
#    pprint.pprint(bucketMap)
#    print bucketStats
    
main()
