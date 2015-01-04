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
        from smartspider.db.mongo_based import MongoDBConnection
        from smartspider.analytics.named_entity_clustering import WORKGRAPH,PERSONALGRAPH
        from smartspider.transport.linkedin import LINKEDIN
        from collections import Counter
        import operator
        db = MongoDBConnection.instance().get_connection().smartspider
        searchterms = self.get_argument("searchterms")
        results = db.command("text","cluster_algo0",search=searchterms)
        results = [res['obj'] for res in results['results']]
        meta_mixed_graph,meta_profile_name,meta_profile_desc,meta_profile_prof = [],[],[],[]
        for a_result in results:
            meta_profile_name.append(a_result['meta_profile_key'].replace("_"," "))
            meta_profile_desc.append(a_result['features'])
            meta_profile_prof.append(a_result['profiles'])
            meta_profile_workgraph = reduce(operator.add,[Counter(a_counter.iteritems()) for a_counter in a_result.get(WORKGRAPH,[{}])], Counter())
            meta_profile_personalgraph = reduce(operator.add,[Counter(a_counter.iteritems()) for a_counter in a_result.get(PERSONALGRAPH,[{}])], Counter())
            worktags = sorted(meta_profile_workgraph,key=meta_profile_workgraph.get,reverse=True)[:6]
            personaltags = sorted(meta_profile_personalgraph,key=meta_profile_personalgraph.get,reverse=True)[:6]
            meta_mixed_graph.append(worktags + personaltags)
                
        return self.render("static/search.html",meta_profile_names = meta_profile_name, meta_profile_desc = meta_profile_desc,
                           meta_profile_prof = meta_profile_prof, meta_mixed_graph = meta_mixed_graph)


class retrieveClusterHandler(BaseHandler):    
    def get(self):  
        from smartspider.db.mongo_based import retrieveCluster
        link = self.get_argument("link")
        namedEntityReco = retrieveCluster("NONE",link)
        ner = namedEntityReco["entity"]
        if 'raw' in ner:
            self.write(ner['raw'])
        else:
            return self.render("static/ner.html",NER=ner['profilesummary'])

class RetrieveMetaProfileHandler(BaseHandler):    
    def get(self):  
        from smartspider.db.mongo_based import findCluster,retrieveClusters
        from smartspider.transport.linkedin import LINKEDIN
        from smartspider.transport.twitter import TWITTER
        from smartspider.transport.meetup import MEETUP
        from smartspider.analytics.named_entity_clustering import WORKGRAPH,PERSONALGRAPH
        import operator
        from collections import Counter        
        link = self.get_argument("link")
        interest=self.get_argument("interest")
        result = findCluster(link)
        all_profiles = [x for x in retrieveClusters("NONE",result['profiles'])]
        linkedin_profile = [x1 for x1 in all_profiles if LINKEDIN in x1['cluster']]
        linkedin_profile = linkedin_profile[0] if linkedin_profile else None
        twitter_profile = [x1 for x1 in all_profiles if TWITTER in x1['cluster']]
        twitter_profile = twitter_profile[0] if twitter_profile else None
        meetup_profile = [x1 for x1 in all_profiles if MEETUP in x1['cluster']]
        meetup_profile = meetup_profile[0] if meetup_profile else None
        name = linkedin_profile['entity']['firstName']+' '+linkedin_profile['entity']['lastName']        
        title = linkedin_profile['entity']['title']
        jobprofilesummary = linkedin_profile['entity']['profilesummary']
        work_interests = linkedin_profile['entity']['interests']
        if jobprofilesummary:
            jobprofilesummary = tornado.escape.xhtml_unescape(jobprofilesummary)
        currentjob = linkedin_profile['entity']['current']
        currentjob = currentjob[0] if currentjob else None
        previous_jobs = linkedin_profile['entity']['previous']
        education = [linkedin_profile['entity']['education']]
        region = linkedin_profile['entity']['region']
        if twitter_profile:
            interests_and_hobbies = twitter_profile['entity']['profilesummary']
            if interests_and_hobbies:
                interests_and_hobbies = tornado.escape.xhtml_unescape(interests_and_hobbies)
            else:
                interests_and_hobbies = ""
            current_tweets = [tornado.escape.xhtml_unescape(x) for x in twitter_profile['entity']['tweets'] if x]
        else:
            interests_and_hobbies = ""
            current_tweets = []
        if meetup_profile:
            org_groups = [tornado.escape.xhtml_unescape(x[0]) for x in meetup_profile['entity']['groups'] if x[1] == 'Organizer']
            memb_groups = [tornado.escape.xhtml_unescape(x[0]) for x in meetup_profile['entity']['groups'] if x[1] == 'Member']
            currentgroups = org_groups + memb_groups
        else:
            currentgroups = []
        return self.render("static/metaprofile.html",meta_name = name, title = title,jobprofilesummary = jobprofilesummary,
                                        currentjob = currentjob,previous_jobs = previous_jobs,
                                        education = education,region = region,work_interests = work_interests,
                                        interests_and_hobbies = interests_and_hobbies,current_tweets=current_tweets,                                                
                                        currentgroups = currentgroups)

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
