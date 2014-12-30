import tornado.ioloop
import tornado.web
import tornado.options
from smartspider.util import log_info_msg
import datetime
from itertools import izip_longest
import os
import tornado.escape

class BaseHandler(tornado.web.RequestHandler):

    def writeJSON(self, chunk):
        assert not self._finished
        if not isinstance(chunk, str):
            chunk = tornado.escape.json_encode(chunk)
            self.set_header("Content-Type", "text/javascript; charset=UTF-8")
        chunk = tornado.escape.utf8(chunk)
        self._write_buffer.append(chunk) 
        
    def get_current_user(self):
        return self.get_secure_cookie("username")

    def get_current_full_name(self):
        return self.get_secure_cookie("FullName")


    def render(self,file,**kwargs):        
        kwargs.update({"FullName":self.get_current_full_name()})
        if self.get_current_full_name():
            log_info_msg("FullName: "+self.get_current_full_name())        
        return super(BaseHandler,self).render(file,**kwargs)


class MainHandler(BaseHandler):    
    def get(self):
        from smartspider.db.mongo_based import MongoDBConnection
        db = MongoDBConnection.instance().get_connection().smartspider
        entries = db.meta_features.find_one()['features']
        tags = sorted(entries,key=entries.get,reverse=True)[:10]
        return self.render("static/home.html",Tags=tags)


    def post(self):
        from smartspider.db.mongo_based import MongoDBConnection
        db = MongoDBConnection.instance().get_connection().smartspider
        searchterms = self.get_argument("searchterms")
        results = db.command("text","cluster_algo0",search=searchterms,limit=100,
                            filter={"$or" : [ { "profiles" : { "$size" : 2 }}, {"profiles" : { "$size" : 3 } }]})
        results = [res['obj'] for res in results['results']]
        meta_profile_name = [x['meta_profile_key'].replace("_"," ") for x in results]
        meta_profile_desc = [x['features'] for x in results]
        meta_profile_prof = [x['profiles'] for x in results]        
        return self.render("static/search.html",meta_profile_names = meta_profile_name, meta_profile_desc = meta_profile_desc,
                           meta_profile_prof = meta_profile_prof)


class RetrieveHandler(BaseHandler):    
    def get(self):  
        from smartspider.db.mongo_based import retrieveCluster
        link = self.get_argument("link")
        namedEntityReco = retrieveCluster("NONE",link)
        ner = namedEntityReco["entity"]
        if 'raw' in ner:
            self.write(ner['raw'])
        else:
            return self.render("static/ner.html",NER=ner['profilesummary'])





settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
}
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/searchprofiles", MainHandler),
    (r"/retrieve", RetrieveHandler),
], **settings)


if __name__ == "__main__":
    import os,sys    
    if sys.platform != "win32":
        tornado.options.options['log_file_prefix'].set('/var/log/talneuro.' + str(os.getpid()))
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()
