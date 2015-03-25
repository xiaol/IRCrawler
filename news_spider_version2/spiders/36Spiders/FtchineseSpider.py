#coding=utf-8
from lxml import etree
from news_spider_version2.items import NewsItem, PartialNewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils
from news_spider_version2.spiders.utils.MongoUtils import MongoUtils


__author__ = 'galois'

import scrapy
import re

import HTMLParser


class FtchineseSpider(scrapy.Spider):
    name='ftchineseSpider'
    allowed_domains=['www.ftchinese.com']

    start_urls=['http://www.ftchinese.com/channel/life.html','http://www.ftchinese.com/channel/pursuit.html']
    # start_urls=['http://youxiputao.com/articles/4545']


    root_class='36度'
    #一级分类下面的频道
    default_channel='同步喜好'
     #源网站的名称
    sourceSiteName='FT中文网'

    default_tag='懂生活'
    tag_map={
        '乐尚街':'拗造型'
    }

    page_url_pattern=re.compile(r'^http://www.ftchinese.com/story/\d+.*')
    non_page_url_pattern=re.compile(r'http://www.ftchinese.com/channel/.*')

    content_pat=re.compile(r'<div(?: [^<>]+)?>\s*<img(?: .*?)? src=".*?"(?: .*?)?></div>|<p(?: [^<>]+)?>.*?</p>')
    img_pat=re.compile(r'<img(?: .*?)? src="(.*?)"(?: .*?)?>')
    para_pat=re.compile(r'<p(?: [^<>]+)?>(.*?)</p>')
    other_page_info_pat=re.compile(r'<a href="(.*?)">\d+</a>')
    previous_page_pat=re.compile(ur'<a href="([\w:/\d\.]+)"(?: [^<>]+?)?>></a>')
    base_url='http://www.ftchinese.com'

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
        # item['imgUrl']=self.extractImgUrl(response)
        item['sourceUrl']=url
        item['sourceSiteName']=self.extractSourceSiteName(response)
        item['tag']=self.extractTag(response)
        item['edit_tag']=self.extractEditTag(response)
        item['channel']=self.extractChannel(response,item)
        item['_id']=self.generateItemId(item)
        item['description']=self.extractDesc(response)
        partialItem=MongoUtils.findPartialItemById(item['_id'])
        item.cloneInfoFromDict(dict(partialItem))
        item.printSelf()
        return item


    def generateItemId(self,item):
        return item['sourceUrl']

    def extractTitle(self,response):
        xpath_str='//div[@class="topic"]/h1[@id="topictitle"]/text()'
        title=response.xpath(xpath_str).extract()[0]
        return title

    def extractTime(self,response):
        xpath_str='//div[@class="topic"]/a[@class="storytime"]/text()'
        raw_time_str=response.xpath(xpath_str).extract()[0]
        time=CrawlerUtils.formatTimeDigitalPat(raw_time_str)
        return time


    def extractRootClass(self,response):
        return self.root_class

    def extractChannel(self,response,item):
        return self.default_channel

    def extractContent(self,response):
        xpath_str='//div[@id="bodytext"]'
        rawContent=response.xpath(xpath_str).extract()[0]
        listInfos=[]
        CrawlerUtils.extractContentList(listInfos,rawContent,self.content_pat,self.img_pat,self.para_pat)
        page_infos=response.xpath('//div[@class="pagination"]/a').extract()
        for other_info in page_infos:
            searchResult=re.search(self.other_page_info_pat,other_info)
            if searchResult:
                url=searchResult.group(1)
                url=self.base_url+url
                url_page_content=CrawlerUtils.getHtmlContentUnicode(url)
                page_dom=etree.HTML(url_page_content)
                contentArr=page_dom.xpath(xpath_str.encode('utf-8'))
                if len(contentArr):
                    rawContent=etree.tostring(contentArr[0],encoding='utf8')
                    CrawlerUtils.extractContentList(listInfos,rawContent,self.content_pat,self.img_pat,self.para_pat)
        return CrawlerUtils.make_img_text_pair(listInfos)

    def extractDesc(self,response):
        return None

    def extractSourceSiteName(self,response):
        return self.sourceSiteName

    #获取文章的tag信息
    def extractTag(self,response):
        xpath_str='//div[@class="info-detail"]/div[@class="tag"]/div[@class="pull-left"]/a/text()'
        tag=response.xpath(xpath_str).extract()
        return tag

    #获取文章的tag信息
    def extractEditTag(self,response):
       xpath_str='//div[@id="header-menu"]/a[@class="link no-border money"]/text()'
       tag_arr=response.xpath(xpath_str).extract()
       if not len(tag_arr):
           return self.default_tag
       if tag_arr[0] in self.tag_map:
           return self.tag_map[tag_arr[0]]
       return self.default_tag

    #处理不是页面的网址
    def dealWithNonPage(self,response,url):
        xpath_str='//div[@id="home-left"]/div[@class="thcover"]'
        page_item_doms=response.xpath(xpath_str)
        base_url='http://www.ftchinese.com'
        request_items=[]
        for elem_dom in page_item_doms:
            page_url=base_url+elem_dom.xpath('./a/@href').extract()[0]
            request_items.append(scrapy.Request(page_url,callback=self.parse,dont_filter=False))
            img_url=elem_dom.xpath('./a/img/@src').extract()[0]
            title=elem_dom.xpath('./a[@class="coverlink"]/text()').extract()[0]
            partialItem=PartialNewsItem()
            partialItem['_id']=page_url
            partialItem['imgUrl']=img_url
            partialItem['title']=title
            MongoUtils.savePartialItem(partialItem)

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

