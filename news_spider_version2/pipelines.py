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
from news_spider_version2.items import NewsItem, PartialNewsItem, NewsProductItem, SimilarItem,GoogleNewsItem,TaskItem,CommentItem
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
        self.titleColl=db[settings['MONGODB_TITLE_COLL']]
        self.taskColl=db[settings['MONGODB_TASK_ITEM_COLL']]
        self.commentColl=db[settings['MONGODB_COMMENT_COLL']]



    def process_item(self, item, spider):
        if type(item) is NewsItem:
            id=item['_id']
            scrapedItem={'_id':id}
            # if self.scrappedColl.find_one(scrapedItem):
            #     log.msg("Item %s alread exists in  database " %(item['_id']),
            #         level=log.DEBUG, spider=spider)
            #     return item
            if id.startswith('http'):
                id=CrawlerUtils.generateId(id)
                item['_id']=id
                scrapedItem={'_id':id}
                # if self.scrappedColl.find_one(scrapedItem):
                #     log.msg("Item %s alread exists in  database " %(item['_id']),
                #         level=log.DEBUG, spider=spider)
                #     return item
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

        elif type(item) is GoogleNewsItem:
            # print "hello"
            # MongoUtils.saveGoogleItem(partial_item)
            # id=item['_id']
            # scrapedItem={'_id':id}
            # if self.scrappedColl.find_one(scrapedItem):
            #     log.msg("Item %s alread exists in  database " %(item['_id']),
            #         level=log.DEBUG, spider=spider)
            #     return item
            print "google&163_news start save"

            if None==item['title']:
                return item
            if len(item['title'])==0:
                return item

            title=item['title']
            titleItem={'title':title}
            if self.googleColl.find_one(titleItem):
                log.msg("Item %s alread exists in  database " %(item['_id']),
                    level=log.DEBUG, spider=spider)
                print "google news alread exists in database"
                return item

            self.googleColl.save(dict(item))
            print "google&163_news end save"
            Task=TaskItem()
            url=item['sourceUrl']
            title=item['title']
            Task['url']=url
            Task['title']=title
            Task['updateTime']=CrawlerUtils.getDefaultTimeStr()

            if item['originsourceSiteName']=='网易新闻图片':
                Task['contentOk']=1
                Task['sourceSiteName']='网易新闻图片'
            else:
                Task['contentOk']=0
                Task['sourceSiteName']='google新闻'

            Task['weiboOk']=0
            Task['zhihuOk']=0
            Task['abstractOk']=0
            Task['nerOk']=0
            Task['baikeOk']=0
            Task['baiduSearchOk']=0
            Task['doubanOk']=0
            Task['relateImgOk']=0
            Task['isOnline']=0

            self.taskColl.save(dict(Task))


        elif type(item) is CommentItem:
            print "google_search start save"
            id=item['_id']
            idItem={'_id':id}
            if self.commentColl.find_one(idItem):
                log.msg("Item %s alread exists in  database " %(item['_id']),
                    level=log.DEBUG, spider=spider)
                print "google_search url alread exists in database"
                return item
            self.commentColl.save(dict(item))
            print "google_search url end save"


        return item
