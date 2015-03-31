#coding=utf-8
from scrapy.conf import settings
from selenium import webdriver
from news_spider_version2.items import NewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils



__author__ = 'galois'

import scrapy
import re

import HTMLParser


class ZhimovieSpider(scrapy.Spider):
    name='zhimovieSpider'
    allowed_domains=['zhihu.com']

    start_urls=['http://zhuanlan.zhihu.com/zhimovie']
    # start_urls=['http://zhuanlan.zhihu.com/zhimovie/19981943']

    root_class='36度'
    #一级分类下面的频道
    default_channel='同步喜好'
     #源网站的名称
    sourceSiteName='知影'

    default_tag='开眼界'

    base_url="http://zhuanlan.zhihu.com"

    page_url_pattern=re.compile(r'^http://zhuanlan.zhihu.com/zhimovie/\d+')
    non_page_url_pattern=re.compile(r'^http://zhuanlan.zhihu.com/zhimovie')

    time_pat=re.compile(r'</a>\s*?@\s*([\d\. ,:]+\w+)\s*?</div>')

    content_pat=re.compile(r'<p(?: [^<>]+?)?>.*?</p>|<img(?: .*?)? src=".*?"(?: .*?)?>')
    img_pat=re.compile(r'<img(?: .*?)? src="(.*?)"(?: .*?)?>')
    para_pat=re.compile(r'p(?: [^<>]+?)?>([^<>]+?)(?:\s*<br>\s*)?</p>')

    previous_page_pat=re.compile(ur'<a href="([\w:/\d\.]+)"(?: [^<>]+?)?>></a>')

    html_parser = HTMLParser.HTMLParser()


    # def start_requests(self):
    #     urls=set([])
    #     for start_url in self.start_urls:
    #         page_urls=self.getPageUrlsFromSelenium(start_url)
    #         if page_urls:
    #             for page_url in page_urls:
    #                 urls.add(page_url)
    #     for url in urls:
    #         yield scrapy.Request(url,callback=self.parse,dont_filter=False)


    def getPageUrlsFromSelenium(self,url):
        caps={
        'takeScreenshot':False,
        'javascriptEnabled':True,
        }

        phantom_link=settings['PHANTOM_LINK']

        driver=webdriver.Remote(
            command_executor=phantom_link,
            desired_capabilities=caps
        )

        driver.get(url)
        # print driver.title
        results=[]
        elems=driver.find_elements_by_xpath('//ul[@class="items"]/li/article/header/a[@class="vote-num ng-binding"]')
        for elem in elems:
            abs_url=elem.get_attribute('href')
            # print "the url is %s" %abs_url
            results.append(abs_url)
        return results


    def parse(self,response):
        url=response._get_url()
        if self.isPage(response,url):
            yield self.dealWithPage(response,url)
        else:
            results=self.dealWithNonPage(response,url)
            # for result in results:
            #     yield(result)

    # def parse(self,response):
    #     url=response._get_url()
    #     page_test=self.isPage(response,url)
    #     #不是要爬取的页面
    #     if page_test==None:
    #         return
    #     if page_test:
    #         yield self.dealWithPage(response,url)
    #     else:
    #         non_page_results,results=self.dealWithNonPage(response,url)
    #         for non_page_result in non_page_results:
    #             yield(non_page_result)
    #         for result in results:
    #             yield(result)

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
        page_driver=self.getSeninumPageDriver(url)
        item['title']=self.extractTitle(page_driver)
        item['content']=self.extractContent(page_driver)
        item['imgUrl']=self.extractImgUrl(page_driver)
        item['sourceUrl']=url
        item['sourceSiteName']=self.extractSourceSiteName(response)
        item['tag']=self.extractTag(response)
        item['edit_tag']=self.extractEditTag(response)
        item['channel']=self.extractChannel(response,item)
        item['_id']=self.generateItemId(item)
        item['description']=self.extractDesc(response)
        item.printSelf()
        return item

    def getSeninumPageDriver(self,url):
        caps={
        'takeScreenshot':False,
        'javascriptEnabled':True,
        }

        phantom_link=settings['PHANTOM_LINK']

        driver=webdriver.Remote(
            command_executor=phantom_link,
            desired_capabilities=caps
        )

        driver.get(url)
        return driver;



    def generateItemId(self,item):
        return item['sourceUrl']

    def extractTitle(self,response):
        xpath_str='//article[@class="entry ng-scope"]/header/h1'
        title=response.find_element_by_xpath(xpath_str).text
        return title


    def extractTime(self,response):
        xpath_str='//div[@class="entry-meta"]/time/@datetime'
        raw_time_strArr=response.xpath(xpath_str).extract()
        if(len(raw_time_strArr)):
            raw_time_str=raw_time_strArr[0]
            return self.formatTime(raw_time_str)

        return CrawlerUtils.getDefaultTimeStr()

    def formatTime(self,raw_time_str):
        time=raw_time_str.split('+')[0].sub('T',' ')
        return time

    def extractRootClass(self,response):
        return self.root_class

    def extractChannel(self,response,item):
        return self.default_channel

    def extractContent(self,response):
        xpath_str='//section[@class="entry-content ng-binding"]'
        rawContent_elem=response.find_element_by_xpath(xpath_str)
        rawContent=rawContent_elem.get_attribute('innerHTML')
        return CrawlerUtils.extractContent(rawContent,self.content_pat,self.img_pat,self.para_pat)


    def extractImgUrl(self,response):
        xpath_str='//div[@class="entry-title-image ng-scope"]/img'
        imgUrlElem=response.find_element_by_xpath(xpath_str)
        if imgUrlElem:
            return imgUrlElem.get_attribute('src')
        return None

    def extractDesc(self,response):
        return None

    def extractSourceSiteName(self,response):
        return self.sourceSiteName

    #获取文章的tag信息
    def extractTag(self,response):
        # xpath_str='//div[@class="note_upper_footer"]/div[@class="footer-tags"]/a/text()'
        # tag=response.xpath(xpath_str).extract()
        # return tag
        tag=[]
        tag.append(self.default_tag)
        return tag

    #获取文章的tag信息
    def extractEditTag(self,response):
        # xpath_str='//div[@class="note_upper_footer"]/div[@class="footer-tags"]/a/text()'
        # tag=response.xpath(xpath_str).extract()
        # return tag
       return self.default_tag;

    #处理不是页面的网址
    def dealWithNonPage(self,response,url):
        return None,None


