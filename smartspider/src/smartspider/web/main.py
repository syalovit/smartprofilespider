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
        tags = sorted(entries,key=entries.get,reverse=True)[:30]
        return self.render("static/home.html",Tags=tags)


    def post(self):
        from smartspider.db.mongo_based import searchCluster
        from smartspider.analytics.named_entity_clustering import genWorkGraph,genPersonalGraph
        searchterms = self.get_argument("searchterms")
        results = searchCluster(searchterms)
        meta_mixed_graph,meta_profile_name,meta_profile_desc,meta_profile_prof = [],[],[],[]
        for a_result in results:
            meta_profile_name.append(a_result['meta_profile_key'].replace("_"," ")) 
            meta_profile_desc.append(a_result['features'])
            meta_profile_prof.append(a_result['profiles'])
            worktags = genWorkGraph(a_result)
            personaltags = genPersonalGraph(a_result)
            meta_mixed_graph.append(worktags + personaltags)
                
        return self.render("static/search.html",meta_profile_names = meta_profile_name, meta_profile_desc = meta_profile_desc,
                           meta_profile_prof = meta_profile_prof, meta_mixed_graph = meta_mixed_graph)


class retrieveClusterHandler(BaseHandler):    
    def get(self):  
        from smartspider.db.mongo_based import retrieveCluster
        link = self.get_argument("link")
        namedEntityReco = retrieveCluster("NONE",link)
        ner = namedEntityReco["entity"]
        if 'raw' in ner and 'linkedin' not in link:
            self.write(ner['raw'])        
        elif 'linkedin' in link:
            return self.redirect(ner['link'])
        else:
            return self.render("static/ner.html",NER=ner['profilesummary'])

class RetrieveMetaProfileHandler(BaseHandler):    
    def get(self):  
        from smartspider.db.mongo_based import findCluster,retrieveClusters,retrieveProfilesFromCluster
        from smartspider.profile.meta_profile_algo0 import MetaProfile
        link = self.get_argument("link")
        interest=self.get_argument("interest")
        
        all_profiles =  retrieveProfilesFromCluster(link)
        meta_prof = MetaProfile(all_profiles) 
        return self.render("static/metaprofile.html",meta_name = meta_prof.name, title = meta_prof.title,jobprofilesummary = meta_prof.jobprofilesummary,
                                        currentjob = meta_prof.currentjob,previous_jobs = meta_prof.previous_jobs or [],
                                        education = meta_prof.education,region = meta_prof.region,work_interests = meta_prof.work_interests or [],
                                        interests_and_hobbies = meta_prof.interests_and_hobbies,current_tweets=meta_prof.current_tweets,                                                
                                        currentgroups = meta_prof.currentgroups)

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
}
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/searchprofiles", MainHandler),
    (r"/retrieve", retrieveClusterHandler),
    (r"/retrieve_meta_profile", RetrieveMetaProfileHandler),
    
], **settings)


if __name__ == "__main__":
    import os,sys    
    if sys.platform != "win32":
        tornado.options.options['log_file_prefix'].set('/var/log/talneuro.' + str(os.getpid()))
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()
