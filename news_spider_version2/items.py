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

    def printSelf(self):
        print " _id is %s" %self['_id']
        print "root_class is %s" %self['root_class']
        print "channel is %s" %self['channel']
        print "content is %s" %self['content']
        print "imgUrl is %s" %self['imgUrl']
        print "updateTime is %s" %self['updateTime']
        print "publisher is %s" %self['publisher']
        print "sourceSiteName is %s" %self['sourceSiteName']
        print "description is %s" %self['description']
        print "sourceUrl is %s" %self['sourceUrl']
