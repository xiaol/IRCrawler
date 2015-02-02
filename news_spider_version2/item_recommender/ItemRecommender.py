#coding=utf-8
import pymongo
from scrapy.conf import settings
from news_spider_version2.item_recommender.SimilarityCaculater import SimilarityCaculater
from operator import itemgetter
from pymongo import ReadPreference
from news_spider_version2.items import SimilarItem


class ItemRecommender:
    connection=pymongo.MongoReplicaSetClient(settings['MONGODB_SERVER'], replicaSet=settings['MONGODB_REPL'],
                                                             read_preference=ReadPreference.PRIMARY)
    db = connection[settings['MONGODB_DB']]
    collection = db[settings['MONGODB_COLLECTION']]
    item_to_item_collection=db[settings['MONGODB_ITEM_TO_ITEM_COLL']]

    @classmethod
    def recommend_by_item(cls,item):
        root_class=item['root_class']
        channel=item['channel']
        candidates=cls.getItems(root_class,channel,1000)

        candidate_score_pairs=[]

        for candidate in candidates:
            item_score=[]
            score=SimilarityCaculater.caculate(item,candidate)
            item_score.append(candidate)
            item_score.append(score)
            candidate_score_pairs.append(item_score)
        candidate_score_pairs.sort(key=itemgetter(1), reverse=True)
        results=[]
        for item in  candidate_score_pairs[0:9]:
            results.append(item[0]['_id'])
        return results


    @classmethod
    def getItems(cls,root_class,channel,num):
        docs = cls.collection.find({"root_class": root_class,"channel":channel}).sort([("updateTime", -1)]).limit(num)
        return docs

    def main(self):
        for item in self.collection.find().sort([("updateTime", -1)]):
            print "itemid is %s" %item['_id']
            results=self.recommend_by_item(item)
            similarItem=SimilarItem()
            similarItem['_id']=item['_id']
            similarItem['similar_items']=results
            self.item_to_item_collection.save(dict(similarItem))

if __name__=='__main__':
    itemRecommender=ItemRecommender()
    print "hello world"
    itemRecommender.main()





