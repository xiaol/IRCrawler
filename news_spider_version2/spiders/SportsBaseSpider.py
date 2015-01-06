#coding=utf-8

import re
import scrapy

from scrapy.conf import settings
from scrapy.http import Request

from news_spider_version2.Text import utils
from news_spider_version2.items import DetailContentItem, PicNewsItem

from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils


class SportsBaseSpider(scrapy.Spider):
    url_pattern=re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    source_site='未知'
    INITIAL_PRIORITY=48*settings['DEPTH_LIMIT']

    disallowed_domains=[]


    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True,priority=self.INITIAL_PRIORITY)

    def parse(self,response):
        res_url=response._get_url()
        if self.isFilteredPage(res_url):
            return

        if self.isPage(response,res_url):
            content=self.extractMainText(response)
            if None==content:
                return
            if len(content):
                picItem=PicNewsItem()
                picItem['content']=content
                title=self.extractTitle(response)
                picItem['title']=title
                desc=self.extractDesc(response)
                if not desc:
                    desc=self.summarization(content)
                picItem['description']=desc.strip()
                imgUrl=self.extractImgUrl(response)
                picItem['imgUrls']=imgUrl
                picItem['category']=self.extractCategory(response)
                picItem['subcategory']=self.extractSubcategory(response)
                picItem['updateTime']=self.extractTime(response)
                picItem['sourceSiteName']=self.getSourceSite(response,res_url)
                picItem['_id']=response._get_url()
                picItem['sourceUrl']=response._get_url()
                picItem['tags']=self.extractTags(response)
                if imgUrl:
                    yield(picItem)
                    detailContentItem=DetailContentItem()
                    detailContentItem['_id']=picItem['_id']
                    detailContentItem['content']=picItem['content']
                    yield(detailContentItem)
                    picItem.printItem()
                    detailContentItem.printItem()
        else:
            request_results=self.dealWtihNonPage(res_url,response)
            if request_results:
                for request_result in request_results:
                    if not self.isFilteredPage(request_result._get_url()):
                        yield request_result

    def isFilteredPage(self,url):
        if None==url:
            return True
        accept=False
        for allowed_domain in self.allowed_domains:
            if allowed_domain in url:
                accept=True
                break
        if not accept:
            return True
        for filtPat in self.disallowed_domains:
            if filtPat in url:
                return True
        return False

    def getSourceSite(self,response,url):
        return self.source_site


    def summarization(self,content):
        if None==content:
            return None
        sentenceArr=content
        i=0
        if len(sentenceArr)>=3:
            i=1
        selectedSentence=self.select_text_from_Infos(sentenceArr[i])
        selectedSentence.replace(CrawlerUtils.Q_space,'')
        selectedSentence.strip()
        descArr=[]
        count=0
        sentenceCount=0
        descBegin=False
        for word in selectedSentence:
            if utils.isNonWord(word):
                if descBegin:
                    descArr.append(word)
                    sentenceCount=sentenceCount+1
            else:
                descBegin=True
                descArr.append(word)
                count=count+1
            if count>=50 | sentenceCount>=3:
                break
        return ''.join(descArr)

    def select_text_from_Infos(self,img_text_tuple):
        for elem in img_text_tuple:
            if 'txt' in elem:
                return elem['txt']
        return None

    def isPage(self,response,url):
        '''
        判断是否是网页
        :param response:
        :param url:
        :return:
        '''
        raise NotImplementedError

    #提取title
    def extractTitle(self,response):
         raise NotImplementedError

    #提取description
    def extractDesc(self,response):
        raise NotImplementedError

    #提取imgurl
    def extractImgUrl(self,response):
         raise NotImplementedError


    #提取正文
    def extractMainText(self,response):
         raise NotImplementedError

    #提取时间
    def extractTime(self,response):
         raise NotImplementedError

    #提取分类
    def extractCategory(self,response):
        raise NotImplementedError
    #提取二级分类
    def extractSubcategory(self,response):
        raise NotImplementedError

    #提取标签tdr
    def extractTags(self,response):
        raise NotImplementedError

    #处理不是页面的网址
    def dealWtihNonPage(self,url,response):
        raise NotImplementedError
