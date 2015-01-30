encoding='utf-8'

__author__ = 'galois'

from scrapy.command import ScrapyCommand
import urllib
import urllib2
from scrapy import log

class AllCrawlCommand(ScrapyCommand):

    requires_project = True
    default_settings = {'LOG_ENABLED':False}



    def short_desc(self):
        return "Schedule a run for all available spiders"

    def run(self,args,opts):
        url='http://localhost:6800/schedule.json'
        crawler = self.crawler_process.create_crawler()
        i=0
        for s in crawler.spiders.list():
            values={'project':'myproject','spider':s}
            data=urllib.urlencode(values)
            req=urllib2.Request(url,data)
            response=urllib2.urlopen(req)
            log.msg(response)

            print "%dth spider is : %s"%(i,s)
            i=i+1


# if __name__=='__main__':
#     cmd=AllCrawlCommand()
#     cmd.run(None,None)