# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsSpiderVersion2Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class NewsItem(scrapy.Item):
    # item 的唯一标识 用源网址
    _id=scrapy.Field()
    #比如0度，36度，等一级分类
    root_class=scrapy.Field()
    #一级分类下面的频道
    channel=scrapy.Field()


    title=scrapy.Field()
    content=scrapy.Field()

     #item 的缩略图
    imgUrl=scrapy.Field()
    #item 生成的时间
    updateTime=scrapy.Field()
    #item 的描述
    description=scrapy.Field()
    sourceUrl=scrapy.Field()
    #源网站的名称
    sourceSiteName=scrapy.Field()
    #网页的tag
    tag=scrapy.Field()
    #edit_tag
    edit_tag=scrapy.Field()
    # 内容的地域
    city=scrapy.Field()


    def printSelf(self):
        print " _id is %s" %self['_id']
        print " title is %s" %self['title']
        print "root_class is %s" %self['root_class']
        print "channel is %s" %self['channel']
        print "content is %s" %self['content']
        print "imgUrl is %s" %self['imgUrl']
        print "updateTime is %s" %self['updateTime']
        print "sourceSiteName is %s" %self['sourceSiteName']
        # print "description is %s" %self['description']
        print "sourceUrl is %s" %self['sourceUrl']
        print "tag is %s" %self['tag']

    def cloneInfoFromDict(self,dict_obj):
        keys=['title','root_class','channel','content','imgUrl',
              'updateTime','sourceSiteName','description','sourceUrl','tag','city']
        if dict_obj==None:
            return
        for key in keys:
            if key in dict_obj:
                self[key]=dict_obj[key]



class GoogleNewsItem(scrapy.Item):
    # item 的唯一标识 用源网址
    _id=scrapy.Field()
    #比如0度，36度，等一级分类
    root_class=scrapy.Field()
    #一级分类下面的频道
    channel=scrapy.Field()
    title=scrapy.Field()
    createTime=scrapy.Field()
     #item 的缩略图
    imgUrl=scrapy.Field()
    #item 生成的时间
    updateTime=scrapy.Field()
    #item 的描述
    description=scrapy.Field()
    sourceUrl=scrapy.Field()
    #源网站的名称
    sourceSiteName=scrapy.Field()
    relate=scrapy.Field()
    originsourceSiteName=scrapy.Field()
    imgWall=scrapy.Field()
    tag=scrapy.Field()




class TaskItem(scrapy.Item):
    # item 的唯一标识 用源网址
    url=scrapy.Field()
    title=scrapy.Field()
    updateTime=scrapy.Field()
    contentOk=scrapy.Field()
    weiboOk=scrapy.Field()
    zhihuOk=scrapy.Field()
    abstractOk=scrapy.Field()
    nerOk=scrapy.Field()
    baikeOk=scrapy.Field()
    baiduSearchOk=scrapy.Field()
    doubanOk=scrapy.Field()
    relateImgOk=scrapy.Field()
    isOnline=scrapy.Field()


class PartialNewsItem(scrapy.Item):
    # item 的唯一标识 用源网址
    _id=scrapy.Field()
    #比如0度，36度，等一级分类
    root_class=scrapy.Field()
    #一级分类下面的频道
    channel=scrapy.Field()
    title=scrapy.Field()
    content=scrapy.Field()
     #item 的缩略图
    imgUrl=scrapy.Field()
    #item 生成的时间
    updateTime=scrapy.Field()
    #item 的描述
    description=scrapy.Field()
    sourceUrl=scrapy.Field()
    #源网站的名称
    sourceSiteName=scrapy.Field()
    #网页的tag
    tag=scrapy.Field()
     # 内容的地域
    city=scrapy.Field()


    def printSelf(self):
        print " _id is %s" %self['_id']
        print "root_class is %s" %self['root_class']
        print "channel is %s" %self['channel']

        print "imgUrl is %s" %self['imgUrl']
        print "updateTime is %s" %self['updateTime']
        print "sourceSiteName is %s" %self['sourceSiteName']
        print "description is %s" %self['description']
        print "sourceUrl is %s" %self['sourceUrl']
        print "tag is %s" %self['tag']


class PicNewsItem(scrapy.Item):
    _id=scrapy.Field()
    title=scrapy.Field()
    content=scrapy.Field()
    imgUrls=scrapy.Field()
    description=scrapy.Field()
    sourceUrl=scrapy.Field()
    updateTime=scrapy.Field()
    sourceSiteName=scrapy.Field()
    category=scrapy.Field()
    subcategory=scrapy.Field()
    keyword=scrapy.Field()
    tags=scrapy.Field()


    def printItem(self):
        print 'title is %s' %self['title']
        print 'content is %s'%self['content']
        print 'description is %s' %self['description']
        print 'imgUrl is %s' %self['imgUrls']
        print 'category is %s' %self['category']
        print 'updateTime is %s' %self['updateTime']
        print 'sourceName is %s' %self['sourceSiteName']

class DetailContentItem(scrapy.Item):
    _id=scrapy.Field()
    content=scrapy.Field()

    def printItem(self):
        print "_id is %s" %self['_id']
        print "content is %s" %self['content']


class NewsProductItem(scrapy.Item):
    # item 的唯一标识 用源网址
    _id=scrapy.Field()
    #r_id
    root_class=scrapy.Field()
    #r_name
    root_name=scrapy.Field()
    #ch_id
    channel=scrapy.Field()
    #ch_name
    channel_name=scrapy.Field()

    title=scrapy.Field()
    content=scrapy.Field()

     #item 的缩略图
    imgUrl=scrapy.Field()
    #item 生成的时间
    updateTime=scrapy.Field()
    #item 的描述
    description=scrapy.Field()
    sourceUrl=scrapy.Field()
    #源网站的名称
    sourceSiteName=scrapy.Field()
    #网页的tag
    tag=scrapy.Field()
    #edit_tag
    edit_tag=scrapy.Field()
    #内容的地域
    city=scrapy.Field()

    def printSelf(self):
        print " _id is %s" %self['_id']
        print " title is %s" %self['title']
        print "root_class is %s" %self['root_class']
        print "channel is %s" %self['channel']
        print "content is %s" %self['content']
        print "imgUrl is %s" %self['imgUrl']
        print "updateTime is %s" %self['updateTime']
        print "sourceSiteName is %s" %self['sourceSiteName']
        print "description is %s" %self['description']
        print "sourceUrl is %s" %self['sourceUrl']
        print "tag is %s" %self['tag']

    def cloneInfoFromDict(self,dict_obj):
        keys=['_id','title','content','imgUrl','updateTime',
              'sourceSiteName','description','sourceUrl','tag','city','edit_tag']
        if dict_obj==None:
            return
        for key in keys:
            if key in dict_obj:
                self[key]=dict_obj[key]


class SimilarItem(scrapy.Item):
    # item 的唯一标识 用源网址
    _id=scrapy.Field()
    similar_items=scrapy.Field()

    def printSelf(self):
        print " _id is %s" %self['_id']

    # def cloneInfoFromDict(self,dict_obj):
    #     keys=['_id','title','content','imgUrl','updateTime',
    #           'sourceSiteName','description','sourceUrl','tag','city']
    #     if dict_obj==None:
    #         return
    #     for key in keys:
    #         if key in dict_obj:
    #             self[key]=dict_obj[key]
