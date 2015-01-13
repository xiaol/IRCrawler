#coding=utf-8
import pymongo
from scrapy.conf import settings
from pymongo import ReadPreference

class MongoUtils:
    # def __init__(self):
    connection=pymongo.MongoReplicaSetClient(settings['MONGODB_SERVER'], replicaSet=settings['MONGODB_REPL'],
                                                             read_preference=ReadPreference.PRIMARY)
    #this line for testing
    # connection = pymongo.Connection(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
    db = connection[settings['MONGODB_DB']]
    collection = db[settings['MONGODB_COLLECTION']]
    scrappedColl=db[settings['MONGODB_CRAWLED_COLLECTION']]
    partialColl=db[settings['MONGODB_PARTIAL_ITEM_COLL']]

    @classmethod
    def findPartialItemById(cls,item_id):
        index={'_id':item_id}
        return cls.partialColl.find_one(index)

    @classmethod
    def savePartialItem(cls,item):
        cls.partialColl.save(dict(item))


