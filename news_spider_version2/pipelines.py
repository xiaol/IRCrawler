# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy import log
from scrapy.conf import settings
from pymongo import ReadPreference
from news_spider_version2.items import NewsItem


class NewsSpiderVersion2Pipeline(object):
    def __init__(self):
        connection=pymongo.MongoReplicaSetClient(settings['MONGODB_SERVER'], replicaSet=settings['MONGODB_REPL'],
                                                             read_preference=ReadPreference.PRIMARY)
        #this line for testing
        # connection = pymongo.Connection(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]
        self.scrappedColl=db[settings['MONGODB_CRAWLED_COLLECTION']]

    def process_item(self, item, spider):
        if type(item) is NewsItem:
            scrapedItem={'_id':item['_id']}
            if self.scrappedColl.find_one(scrapedItem):
                log.msg("Item %s alread exists in  database " %(item['_id']),
                    level=log.DEBUG, spider=spider)
                return item
            self.collection.save(dict(item))

            self.scrappedColl.save(scrapedItem)
            log.msg("Item wrote to MongoDB database %s/%s" %(settings['MONGODB_DB'], settings['MONGODB_COLLECTION']),
                    level=log.DEBUG, spider=spider)
        return item
