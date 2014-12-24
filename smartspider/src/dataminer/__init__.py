from db.file_based import  read_basic_cluster

def main():
    bucketMap = read_basic_cluster()
    import pprint
    pprint.pprint(bucketMap)
    
main()
