#coding=utf-8
import pymongo
from scrapy.conf import settings
from pymongo import ReadPreference

class MongoUtils:
    # def __init__(self):
    connection=pymongo.MongoReplicaSetClient(settings['MONGODB_SERVER'], replicaSet=settings['MONGODB_REPL'],
                                                             read_preference=ReadPreference.PRIMARY)

    db = connection[settings['MONGODB_DB']]
    collection = db[settings['MONGODB_COLLECTION']]
    scrappedColl=db[settings['MONGODB_CRAWLED_COLLECTION']]
    partialColl=db[settings['MONGODB_PARTIAL_ITEM_COLL']]

    googleColl=db[settings['MONGODB_GOOGLE_ITEM_COLL']]
    product_collection=db[settings['MONGODB_PRODUCT_COLLECTION']]
    root_info_coll=db[settings['MONGODB_ROOT_INFO_COLL']]

    root_coll = db[settings['MONGODB_ROOT_INFO_COLL']]
    r_alias=['-40度','0度','36度','40度']
    r_name=['你未见的时代冰点','你不知道的冷新闻','同步你的关注热度','触摸时下热点']
    ch_infos=[
        [{'ch_id':0,'ch_name':'让坚冰在这里消融','alias':'冰封'},
         {'ch_id':1,'ch_name':'镜头抽离改变了谁','alias':'镜头'}],

        [{'ch_id':0,'ch_name':'不妨看点儿冷新闻','alias':'冷新闻'},
         {'ch_id':1,'ch_name':'冷知识也会有春天','alias':'冷知识'},
         {'ch_id':2,'ch_name':'人人都是冷面笑匠','alias':'冷幽默'}],

        [{'ch_id':0,'ch_name':'快打开新闻和暖气','alias':'同步喜好'},
         {'ch_id':1,'ch_name':'有种温暖直击人心','alias':'暖心'},
         {'ch_id':2,'ch_name':'不在城市也知城事','alias':'城市'}],

        [{'ch_id':0,'ch_name':'最热门的要趁热看','alias':'最热门'},
         {'ch_id':1,'ch_name':'没有热播剧的日子','alias':'热播剧'},
         {'ch_id':2,'ch_name':'数码科技热辣点评','alias':'数码科技'}]
    ]


    @classmethod
    def findPartialItemById(cls,item_id):
        index={'_id':item_id}
        return cls.partialColl.find_one(index)

    @classmethod
    def savePartialItem(cls,item):
        cls.partialColl.save(dict(item))

    @classmethod
    def saveGoogleItem(cls,item):
        cls.googleColl.save(dict(item))

    #返回item的 root_id ,root_name,channel_id,channel_name
    @classmethod
    def findRootInfo(cls,root_alias,ch_alias):
        u_root_alias=root_alias.decode('utf-8')
        u_ch_alias=ch_alias.decode('utf-8')
        filt={'alias':u_root_alias}
        info=cls.root_info_coll.find_one(filt)
        if info==None:
            return None,None,None,None
        rid=info['rid']
        r_name=info['r_name']
        list_chs=info['channelInfos']
        for ch_info in list_chs:
            if u_ch_alias==ch_info['alias']:
                return rid,r_name,ch_info['ch_id'],ch_info['ch_name']


    @classmethod
    def makeRootInfoTable(cls):
        i=0
        for root_alia in cls.r_alias:
            root_info={}
            root_info['rid']=i
            root_info['alias']=root_alia
            root_info['r_name']=cls.r_name[i]
            root_info['channelInfos']=cls.ch_infos[i]
            cls.root_coll.save(root_info)
            i=i+1

if __name__=='__main__':
    # MongoUtils.makeRootInfoTable()
    print 'Hello world'

