#coding=utf-8
from scrapy import cmdline
from scrapy.conf import settings
from scrapy.command import ScrapyCommand
import time

class AllSpiderNameCommand(ScrapyCommand):
    requires_project = True
    default_settings = {'LOG_ENABLED':True}
    SCORE_INC=settings['DEPTH_LIMIT']+1


    def short_desc(self):
        return "run all the commands"

    def run(self,args,opts):
        crawler = self.crawler_process.create_crawler()
        file=open('spider_run_time.txt','a')
        start=time.clock()
        file.write("starting time is \n ")
        file.write(str(start))
        file.write("\n")
        for spider in crawler.spiders.list():
            print spider
            argv=[]
            argv.append('cmdline')
            argv.append('crawl')
            argv.append(spider)
            # cmdline.execute(argv=argv);
        elapsed=time.clock()-start
        file.write("the elapsed time is \n")
        file.write(str(elapsed))
        file.write("\n")
        file.close()

