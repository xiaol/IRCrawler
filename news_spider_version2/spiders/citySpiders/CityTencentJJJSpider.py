#coding=utf-8
import json
from news_spider_version2.items import NewsItem, PartialNewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils
from news_spider_version2.spiders.utils.MongoUtils import MongoUtils


__author__ = 'galois'

import scrapy
import re

import HTMLParser


class CityTencentJJJSpider(scrapy.Spider):
    name='CityTencentJJJ'
    allowed_domains=['jjj.qq.com']

    start_urls=['http://tj.jjj.qq.com/news']

    # start_urls=['http://bj.jjj.qq.com/a/20150114/015880.htm']

    root_class='36度'
    #一级分类下面的频道
    default_channel='城市'
     #源网站的名称
    sourceSiteName='腾讯大燕网'
    default_city="北京"


    url_pattern=re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    page_url_pattern=re.compile(r'^http://pansci.tw/archives/\d+$')

    total_pages_pattern=re.compile(r'<span class="page-ch">.*?(\d+).*?</span>')
    page_lists_pat=re.compile(r'<a href="(.*?)" class="page-en">\d+</a>')

    time_pat=re.compile(r'</a>\s*?@\s*([\d\. ,:]+\w+)\s*?</div>')
    digital_pat=re.compile(r'\d+')

    content_pat=re.compile(r'<p(?: .*?)?>.*?</p>')
    img_pat=re.compile(r'<img(?: .*?)? src="(.*?)"(?: .*?)?>')
    para_pat=re.compile(r'<p style="TEXT-INDENT.*?">(.+?)</p>')

    previous_page_pat=re.compile(ur'<a href="([\w:/\d\.]+)"(?: [^<>]+?)?>></a>')
    city_str_pat=re.compile(r'http://(\w+)\.')
    base_url_pat=re.compile(r'(http[s]?://[\w\d\.]+)/')

    html_parser = HTMLParser.HTMLParser()
    city_map={'bj':'北京','tj':'天津'}

    def parse(self,response):
        url=response._get_url()
        if self.isPage(response,url):
            yield self.dealWithPage(response,url)
        else:
            results=self.dealWithNonPage(response,url)
            for result in results:
                yield(result)

    def isPage(self,response,url):
        if None==url:
            return False
        return url.endswith('.htm')
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
        raw_time_str=response.xpath('//div[@class="ll"]/span[@class="article-time"]/text()').extract()[0]
        time=raw_time_str
        return self.formatTime(time)

    def formatTime(self,timeStr):
        defaultTimeStr=CrawlerUtils.getDefaultTimeStr()
        time=timeStr+":"+defaultTimeStr.split(":")[-1]
        return time

    def extractRootClass(self,response):
        return self.root_class

    def extractChannel(self,response,item):
        return self.default_channel

    def extractContent(self,response):
        xpathStr='//div[@class="main"]/div[@id="C-Main-Article-QQ"]/div/div[@id="Cnt-Main-Article-QQ"]'
        rawContent=response.xpath(xpathStr).extract()[0]
        return CrawlerUtils.extractContent(rawContent,self.content_pat,self.img_pat,self.para_pat)

    def extractCity(self,response,url):
        if None==url:
            return self.default_city
        matchResult=re.match(self.city_str_pat,url)
        if matchResult:
            city_str=matchResult.group(1)
            if city_str in self.city_map:
                return self.city_map[city_str]
            return self.default_city



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
        return None

    #处理不是页面的网址
    def dealWithNonPage(self,response,url):
        pages_tags=response.xpath('//div[@class="layout bline"]/div/div[@class="hd"]/h2/text()').extract()
        pages_arr=response.xpath('//div[@class="layout bline"]/div/div[@class="bd"]/ul')
        partial_page_items=[]
        city=self.extractCity(response,url)
        request_items=[]
        i=0
        for elem_dom in pages_arr:
            tag=[]
            tag.append(pages_tags[i])
            elems=elem_dom.xpath('./li')
            for elem in elems:
                partial_item=self.generatePartialItem(elem,tag,city,url)
                if partial_item:
                    # partial_page_items.append(partial_item)
                    MongoUtils.savePartialItem(partial_item)
                    print "souceUrl is %s" %partial_item['sourceUrl']
                    request_items.append(scrapy.Request(partial_item['sourceUrl'],callback=self.parse,dont_filter=False))
        return request_items

    def generatePartialItem(self,dom_elem,tag,city,parentUrl):
        partial_item=PartialNewsItem()
        partial_item['tag']=tag
        partial_item['city']=city
        print "city is %s" %city


        source_url_arr=dom_elem.xpath('./a/@href').extract()
        if not len(source_url_arr):
            return None
        source_url=source_url_arr[0]
        if  not source_url.startswith('http'):
            baseUrl=self.extractBaseUrl(parentUrl)
            if baseUrl:
                source_url=baseUrl+source_url
        partial_item['sourceUrl']=source_url
        partial_item['_id']=source_url
        partial_item['imgUrl']=dom_elem.xpath('./a/img/@src').extract()[0]
        partial_item['title']=dom_elem.xpath('./div[@class="info"]/h2/a/text()').extract()[0]
        partial_item['description']=dom_elem.xpath('./div[@class="info"]/p/text()').extract()[0]
        return partial_item

    #提取当前页面的文件夹路径
    def extractBaseUrl(self,url):
        if None==url:
            return None
        matchResult=re.match(self.base_url_pat,url)
        if matchResult:
            return matchResult.group(1)
        return None


    #  #获取前面一页的url
    # def getPrevoiuPageUrl(self,response):
    #     previousUrlsPath=response.xpath('//div[@class="pagging"]/div[@class="pagging_inside"]').extract()
    #     if len(previousUrlsPath):
    #         html_parser=HTMLParser.HTMLParser()
    #         page_url_str=html_parser.unescape(previousUrlsPath[0])
    #
    #         search_result=re.search(self.previous_page_pat,page_url_str)
    #         if search_result:
    #             return search_result.group(1)
    #     return None



    def main(self,url):
       urlStr=self.getHtmlContentUnicode(url)
       print urlStr

if __name__=='__main__':
    some_interface='http://jandan.duoshuo.com/api/threads/listPosts.json?thread_key=comment-2650694&url=http%3A%2F%2Fjandan.net%2Fooxx%2Fpage-1301%26yid%3Dcomment-2650694&image=http%3A%2F%2Fww1.sinaimg.cn%2Fmw600%2Fa00dfa2agw1enxg54qbbfj20n40x6755.jpg&require=site%2Cvisitor%2Cnonce%2CserverTime%2Clang&site_ims=1420356603&lang_ims=1420356603&v=140327'
    print "the interface is %s"%some_interface
    html_parser=HTMLParser.HTMLParser()
    print "the unscaped is %s " %html_parser.unescape(some_interface)
