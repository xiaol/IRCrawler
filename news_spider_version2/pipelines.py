# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy import log
from scrapy.conf import settings
from pymongo import ReadPreference
from news_spider_version2.item_recommender.ItemRecommender import ItemRecommender
from news_spider_version2.items import NewsItem, PartialNewsItem, NewsProductItem, SimilarItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils
from news_spider_version2.spiders.utils.MongoUtils import MongoUtils


class NewsSpiderVersion2Pipeline(object):
    def __init__(self):
        connection=pymongo.MongoReplicaSetClient(settings['MONGODB_SERVER'], replicaSet=settings['MONGODB_REPL'],
                                                             read_preference=ReadPreference.PRIMARY)
        #this line for testing
        # connection = pymongo.Connection(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]
        self.scrappedColl=db[settings['MONGODB_CRAWLED_COLLECTION']]
        self.partialColl=db[settings['MONGODB_PARTIAL_ITEM_COLL']]
        self.product_collection=db[settings['MONGODB_PRODUCT_COLLECTION']]
        self.item_to_item_collection=db[settings['MONGODB_ITEM_TO_ITEM_COLL']]
        self.googleColl=db[settings['MONGODB_GOOGLE_ITEM_COLL']]


    def process_item(self, item, spider):
        if type(item) is NewsItem:
            id=item['_id']
            scrapedItem={'_id':id}
            if self.scrappedColl.find_one(scrapedItem):
                log.msg("Item %s alread exists in  database " %(item['_id']),
                    level=log.DEBUG, spider=spider)
                return item
            if id.startswith('http'):
                id=CrawlerUtils.generateId(id)
                item['_id']=id
                scrapedItem={'_id':id}
                if self.scrappedColl.find_one(scrapedItem):
                    log.msg("Item %s alread exists in  database " %(item['_id']),
                        level=log.DEBUG, spider=spider)
                    return item
            if None==item['content']:
                return item
            if len(item['content'])==0:
                return item
            item_dict=dict(item)
            item_dict['_id']=id
            self.collection.save(item_dict)
            self.scrappedColl.save(scrapedItem)
            log.msg("Item wrote to MongoDB database %s/%s" %(settings['MONGODB_DB'], settings['MONGODB_COLLECTION']),
                    level=log.DEBUG, spider=spider)
            similarItem=SimilarItem()
            similarItem['_id']=id
            recommend_items=ItemRecommender.recommend_by_item(item)
            similarItem['similar_items']=recommend_items
            self.item_to_item_collection.save(dict(similarItem))

            #save the item to product collection
            product_item=NewsProductItem()
            product_item.cloneInfoFromDict(item_dict)
            rid,r_name,cid,c_name=MongoUtils.findRootInfo(item_dict['root_class'],item_dict['channel'])
            product_item['root_class']=rid
            product_item['root_name']=r_name
            product_item['channel']=cid
            product_item['channel_name']=c_name
            self.product_collection.save(dict(product_item))



        elif type(item) is PartialNewsItem:
            self.partialColl.save(dict(item))

        return item
