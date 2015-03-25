#coding=utf-8
from news_spider_version2.items import NewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils



__author__ = 'galois'

import scrapy
import re

import HTMLParser


class YouxiputaoSpider(scrapy.Spider):
    name='youxiputaoSpider'
    allowed_domains=['youxiputao.com']

    start_urls=['http://youxiputao.com/article/topic/id/2','http://youxiputao.com/article/topic/id/6']
    # start_urls=['http://youxiputao.com/articles/4545']


    root_class='36度'
    #一级分类下面的频道
    default_channel='同步喜好'
     #源网站的名称
    sourceSiteName='游戏葡萄'

    default_tag='玩出范'

    page_url_pattern=re.compile(r'^http://youxiputao.com/articles/\d+')
    non_page_url_pattern=re.compile(r'http://youxiputao.com/article/topic(/page/\d+)?/id/\d+')

    time_pat=re.compile(r'</a>\s*?@\s*([\d\. ,:]+\w+)\s*?</div>')

    content_pat=re.compile(r'<p(?: [^<>]+)?>.*?</p>|<h2>.*?</h2>')
    img_pat=re.compile(r'<img(?: .*?)? src="(.*?)"(?: .*?)?>')
    para_pat=re.compile(r'<p>(.*?)</p>|<h2>(.*?)</h2>')

    previous_page_pat=re.compile(ur'<a href="([\w:/\d\.]+)"(?: [^<>]+?)?>></a>')

    html_parser = HTMLParser.HTMLParser()

    def parse(self,response):
        url=response._get_url()
        page_test=self.isPage(response,url)
        #不是要爬取的页面
        if page_test==None:
            return
        if page_test:
            yield self.dealWithPage(response,url)
        else:
            non_page_results,results=self.dealWithNonPage(response,url)
            for non_page_result in non_page_results:
                yield(non_page_result)
            for result in results:
                yield(result)

    def isPage(self,response,url):
        if None==url:
            return None
        if re.match(self.page_url_pattern,url):
            return True
        elif re.match(self.non_page_url_pattern,url):
            return False
        return None


    def dealWithPage(self,response,url):
        # item 的唯一标识 用源网址
        item=NewsItem()

        item['root_class']=self.extractRootClass(response)

        item['updateTime']=self.extractTime(response)
        item['title']=self.extractTitle(response)
        item['content']=self.extractContent(response)
        item['imgUrl']=self.extractImgUrl(response)
        item['sourceUrl']=url
        item['sourceSiteName']=self.extractSourceSiteName(response)
        item['tag']=self.extractTag(response)
        item['edit_tag']=self.extractEditTag(response)
        item['channel']=self.extractChannel(response,item)
        item['_id']=self.generateItemId(item)
        item['description']=self.extractDesc(response)
        item.printSelf()
        return item


    def generateItemId(self,item):
        return item['sourceUrl']

    def extractTitle(self,response):
        xpath_str='//div[@class="title-box"]/h2/text()'
        title=response.xpath(xpath_str).extract()[0]
        return title

    def extractTime(self,response):
        xpath_str='//div[@class="title-box"]/div[@class="pull-left"]/div[@class="time"]/b/text()'
        raw_time_str=response.xpath(xpath_str).extract()[0]
        time=self.formatTime(raw_time_str)
        return time

    def formatTime(self,raw_time_str):
        raw_time_arr=raw_time_str.split(' ')
        year_to_day=raw_time_arr[-1]
        return year_to_day+' '+CrawlerUtils.getDefaultTimeStr().split(' ')[-1]


    def extractRootClass(self,response):
        return self.root_class

    def extractChannel(self,response,item):
        return self.default_channel

    def extractContent(self,response):
        xpath_str='//div[@class="info-detail"]/div[@class="info"]'
        rawContent=response.xpath(xpath_str).extract()[0]
        return CrawlerUtils.extractContent(rawContent,self.content_pat,self.img_pat,self.para_pat,base_url='http://youxiputao.com')


    def extractImgUrl(self,response):
        xpath_str='//div[@class="cover"]/img/@src'
        img_url_arr=response.xpath(xpath_str).extract()
        if len(img_url_arr):
            return img_url_arr[0]
        return None

    def extractDesc(self,response):
        return None

    def extractSourceSiteName(self,response):
        return self.sourceSiteName

    #获取文章的tag信息
    def extractTag(self,response):
        xpath_str='//div[@class="info-detail"]/div[@class="tag"]/div[@class="pull-left"]/a/text()'
        tag=response.xpath(xpath_str).extract()
        return tag

        # tag=[]
        # tag.append(self.default_tag)
        # return tag

    #获取文章的tag信息
    def extractEditTag(self,response):
        # xpath_str='//div[@class="note_upper_footer"]/div[@class="footer-tags"]/a/text()'
        # tag=response.xpath(xpath_str).extract()
        # return tag
       return self.default_tag;

    #处理不是页面的网址
    def dealWithNonPage(self,response,url):
        xpath_str='//div[@class="news-box"]/ul[@class="row hidden-xs"]/li/a/@href'
        pages_arr=response.xpath(xpath_str).extract()
        request_items=[]
        base_url='http://youxiputao.com'
        for elem in pages_arr:
            request_items.append(scrapy.Request(base_url+elem,callback=self.parse,dont_filter=False))

        non_page_results=[]
        non_page_url=self.getPrevoiuPageUrl(response)
        if non_page_url:
            non_page_results.append(scrapy.Request(non_page_url,callback=self.parse,dont_filter=False))
        return non_page_results,request_items


     #获取前面一页的url
    def getPrevoiuPageUrl(self,response):
        # xpath_str='//div[@class="news-box"]/ul[@class="row hidden-xs"]/li/a/@href'
        # previousUrlsPath=response.xpath(xpath_str).extract()
        # if len(previousUrlsPath):
        #     html_parser=HTMLParser.HTMLParser()
        #     page_url_str=html_parser.unescape(previousUrlsPath[0])
        #     return page_url_str
        return None



