#coding=utf-8
import json
from news_spider_version2.items import NewsItem, PartialNewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils
from news_spider_version2.spiders.utils.MongoUtils import MongoUtils


__author__ = 'galois'

import scrapy
import re

import HTMLParser


class WeixinSougouSpider(scrapy.Spider):
    name='WeixinSougou'
    allowed_domains=['weixin.sogou.com','mp.weixin.qq.com']

    start_urls=['http://weixin.sogou.com/gzh?openid=oIWsFt5HJEgGlbxXAB2hBcmwjQho']

    # start_urls=['http://pansci.tw/archives/category/type/living']

    # start_urls=['http://pansci.tw/archives/70656']

    root_class='36度'
    #一级分类下面的频道
    default_channel='和暖气'
     #源网站的名称
    sourceSiteName='知乎日报'

    default_tag='涨姿势'

    page_url_pattern=re.compile(r'^http://mp.weixin.qq.com/s?__biz=.*')

    time_pat=re.compile(r'</a>\s*?@\s*([\d\. ,:]+\w+)\s*?</div>')
    digital_pat=re.compile(r'\d+')

    content_pat=re.compile(r'<p>.*?</p>|<img(?: .*?)? src=".*?"(?: .*?)?>')
    img_pat=re.compile(r'<img(?: .*?)? src="(.*?)"(?: .*?)?>')
    para_pat=re.compile(r'<p>(.+?)</p>')

    previous_page_pat=re.compile(ur'<a href="([\w:/\d\.]+)"(?: [^<>]+?)?>></a>')

    html_parser = HTMLParser.HTMLParser()

    def parse(self,response):
        url=response._get_url()
        if self.isPage(response,url):
            yield self.dealWithPage(response,url)
        else:
            results=self.dealWithNonPage(response,url)
            # for result in results:
            #     yield(result)

    def isPage(self,response,url):
        if None==url:
            return False
        if re.match(self.page_url_pattern,url):
            return True
        return False


    def dealWithPage(self,response,url):
        # item 的唯一标识 用源网址
        item=NewsItem()

        item['root_class']=self.extractRootClass(response)

        item['updateTime']=self.extractTime(response)
        # item['title']=self.extractTitle(response)
        item['content']=self.extractContent(response)
        # item['imgUrl']=self.extractImgUrl(response)
        item['sourceUrl']=url
        item['sourceSiteName']=self.extractSourceSiteName(response)
        item['tag']=self.extractTag(response)
        item['channel']=self.extractChannel(response,item)
        item['_id']=self.generateItemId(item)
        dict_obj=MongoUtils.findPartialItemById(item['_id'])
        item.cloneInfoFromDict(dict_obj)

        item.printSelf()
        return item


    def generateItemId(self,item):
        return item['sourceUrl']

    # def extractTitle(self,response):
    #     title=response.xpath('//div[@class="post f"]/h1/a/text()').extract()[0]
    #     return title

    def extractTime(self,response):
        raw_time_str=response.xpath('//meta[@name=\'shareaholic:article_modified_time\']/@content').extract()[0]
        time=raw_time_str
        return self.formatTime(time)

    def formatTime(self,timeStr):
        time=timeStr.split('+')[0].strip().replace('T',' ')
        return time

    def extractRootClass(self,response):
        return self.root_class

    def extractChannel(self,response,item):
        return self.default_channel

    def extractContent(self,response):
        rawContent=response.xpath('//div[@class="pure_content"]').extract()[0]
        return CrawlerUtils.extractContent(rawContent,self.content_pat,self.img_pat,self.para_pat)


    # def extractImgUrl(self,response):
    #     rawContent=response.xpath('//div[@class="post f"]').extract()
    #     if not len(rawContent):
    #         return None
    #     for line in re.findall(self.content_pat,rawContent[0]):
    #         imgSearch=re.search(self.img_pat,line)
    #         if imgSearch:
    #             return imgSearch.group(1)
    #     return None

    # def extractDesc(self,response):
    #     return None

    def extractSourceSiteName(self,response):
        return self.sourceSiteName

    #获取文章的tag信息
    def extractTag(self,response):
        tag=response.xpath('//ul[@class="post-tags"]/li/a[@rel="tag"]/text()').extract()
        return tag

    #处理不是页面的网址
    def dealWithNonPage(self,response,url):
        pages_arr=response.xpath('//div[@class="result"]').extract()
        request_items=[]
        for elem in pages_arr:
            request_items.append(scrapy.Request(elem,callback=self.parse,dont_filter=False))
            print "the child url is %s"%elem

        return request_items

    def generatePartialItem(self,dom_elem):
        partial_item=PartialNewsItem()

        source_url_arr=dom_elem.xpath('./div[@class="image"]/a/@href').extract()
        if not len(source_url_arr):
            return None
        source_url=source_url_arr[0]
        partial_item['sourceUrl']=source_url
        partial_item['_id']=source_url
        partial_item['imgUrl']=dom_elem.xpath('./div[@class="image"]/a/img/@src').extract()[0]
        partial_item['title']=dom_elem.xpath('./div[@class="image"]/a/@title').extract()[0]
        partial_item['description']=dom_elem.xpath('./div[@class="information"]/p/text()').extract()[0]
        return partial_item

     #获取前面一页的url
    def getPrevoiuPageUrl(self,response):
        previousUrlsPath=response.xpath('//div[@class="pagging"]/div[@class="pagging_inside"]').extract()
        if len(previousUrlsPath):
            html_parser=HTMLParser.HTMLParser()
            page_url_str=html_parser.unescape(previousUrlsPath[0])

            search_result=re.search(self.previous_page_pat,page_url_str)
            if search_result:
                return search_result.group(1)
        return None



    def main(self,url):
       urlStr=self.getHtmlContentUnicode(url)
       print urlStr

if __name__=='__main__':
    some_interface='http://jandan.duoshuo.com/api/threads/listPosts.json?thread_key=comment-2650694&url=http%3A%2F%2Fjandan.net%2Fooxx%2Fpage-1301%26yid%3Dcomment-2650694&image=http%3A%2F%2Fww1.sinaimg.cn%2Fmw600%2Fa00dfa2agw1enxg54qbbfj20n40x6755.jpg&require=site%2Cvisitor%2Cnonce%2CserverTime%2Clang&site_ims=1420356603&lang_ims=1420356603&v=140327'
    print "the interface is %s"%some_interface
    html_parser=HTMLParser.HTMLParser()
    print "the unscaped is %s " %html_parser.unescape(some_interface)