def log_important_msg(msg):    
    try:
        import logging
        print msg
        logging.getLogger().log(logging.ERROR,msg)
    except:
        pass
    
def log_info_msg(msg):
    try:
        import logging
        print msg
        logging.getLogger().log(logging.INFO,msg)
    except:
        pass
    
def set_logging_level_debug():
    import logging
    logging.getLogger().setLevel(logging.INFO)
    import sys,os    
    log_path = 'C:\\TEMP\\' if sys.platform == 'win32' else '/tmp/'
    prog_name = sys.argv[0].split('\\')[-1] if sys.platform == 'win32' else sys.argv[0].split('/')[-1]
    logging.basicConfig(filename=log_path+"smartspider_"+prog_name+"_"+str(os.getpid())+".log",filemode="a+",format='%(asctime)s %(message)s')

def set_logging_level_prod():
    import logging
    logging.getLogger().setLevel(logging.ERROR)
    
