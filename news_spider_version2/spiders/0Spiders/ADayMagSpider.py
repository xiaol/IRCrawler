#coding=utf-8
import HTMLParser
import re
import scrapy
from news_spider_version2.items import NewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils

__author__ = 'galois'

class ADayMagSpider(scrapy.Spider):
    name='ADayMagSpider'
    allowed_domains=['www.adaymag.com']

    # start_urls=['http://www.adaymag.com/worldpost/fun/',
    #             'http://www.adaymag.com/lifestyle/pet/','http://www.adaymag.com/kids/']
    start_urls=['http://www.adaymag.com/kids/','http://www.adaymag.com/lifestyle/pet/',
                'http://www.adaymag.com/worldpost/heartwarming/','http://www.adaymag.com/worldpost/fun/']

    # start_urls=['http://www.adaymag.com/2015/02/28/7-images-almost-freaky-thedress.html']

    root_class='0度'
    #一级分类下面的频道
    default_channel='冷幽默'
     #源网站的名称
    sourceSiteName='時尚生活雜誌'


    time_pat=re.compile(r'</a>\s*?@\s*([\d\. ,:]+\w+)\s*?</div>')

    content_pat=re.compile(r'<p>.*?</p>|<h4>.*?</h4>',re.DOTALL)
    img_pat=re.compile(r'<img(?: .*?)? src="(.*?)"(?: [^<>]+?)?>',re.DOTALL)
    para_pat=re.compile(r'<p>(.+?)</p>|<h4>(.+?)</h4>',re.DOTALL)

    previous_page_pat=re.compile(r'<a href="(.*?)">»</a>')


    html_parser = HTMLParser.HTMLParser()

    root_class_map={
        '溫情':'36度',
        '宠物':'36度',
        'KIDS':'36度',
        '寵物':'36度',
        '趣聞':'0度'
    }

    channel_map={
        '溫情':'暖心',
        '宠物':'暖心',
        'KIDS':'暖心',
        '趣聞':'冷幽默'
    }

    def parse(self,response):

        url=response._get_url()
        if self.isPage(response,url):
            yield self.dealWithPage(response,url)
        else:
            results=self.dealWtihNonPage(response,url)
            for result in results:
                yield(result)


    def isPage(self,response,url):
        if None==url:
            return False
        if url.endswith(".html"):
            return True
        return False


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
        item['description']=self.extractDesc(response)
        item['channel']=self.extractChannel(response,item)
        item['_id']=self.generateItemId(item)

        item.printSelf()
        return item


    def generateItemId(self,item):
        return item['sourceUrl']

    def extractTitle(self,response):
        xpath_str='//header/h1/text()'
        title=response.xpath(xpath_str).extract()[0]
        title=self.html_parser.unescape(title).strip()
        return title

    def extractTime(self,response):
        xpath_str='//header/div[@class="meta-info"]/time/@datetime'
        raw_time_str=response.xpath(xpath_str).extract()[0]
        return self.formatTime(raw_time_str)

    def formatTime(self,timeStr):
        raw_time_str=timeStr.split('+')[0]
        result=raw_time_str.replace('T',' ')
        return result

    def extractRootClass(self,response):
        xpath_str='//div[@class="entry-crumbs"]/span/a/span/text()'
        ct_array=response.xpath(xpath_str).extract()
        if len(ct_array):
            raw_tag=ct_array[-1].encode('utf-8')
            if raw_tag in self.root_class_map:
                return self.root_class_map[raw_tag]
        return self.root_class

    def extractChannel(self,response,item):
        xpath_str='//div[@class="entry-crumbs"]/span/a/span/text()'
        ct_array=response.xpath(xpath_str).extract()
        if len(ct_array):
            raw_tag=ct_array[-1].encode('utf-8')
            if raw_tag in self.channel_map:
                return self.channel_map[raw_tag]
        return self.default_channel


    def extractContent(self,response):
        xpath_str='//div[@class="td-post-text-content"]/span[@id="innity-in-post"]'
        rawContent=response.xpath(xpath_str).extract()
        if not len(rawContent):
            return None
        return CrawlerUtils.extractContent(rawContent[0],self.content_pat,self.img_pat,self.para_pat,base_url='http:')


    def extractImgUrl(self,response):
        xpath_str='//*[@id="post-268441"]/div/div/div/div/div/div[1]/div/div/div[2]/a/img/@src'
        img_arr=response.xpath(xpath_str).extract()
        if len(img_arr):
            return 'http:'+img_arr[0]
        xpath_str='//div[@class="td-post-text-content"]/span[@id="innity-in-post"]'
        rawContent=response.xpath(xpath_str).extract()
        if not len(rawContent):
            return None
        for line in re.findall(self.content_pat,rawContent[0]):
            imgSearch=re.search(self.img_pat,line)
            if imgSearch:
                return 'http:'+imgSearch.group(1)
        return None

    def extractDesc(self,response):
        return None

    def extractSourceSiteName(self,response):
        return self.sourceSiteName

    #获取文章的tag信息
    def extractTag(self,response):
        xpath_str='//div[@class="meta-info"]/ul[@class="td-category"]/li/a/text()'
        tag=response.xpath(xpath_str).extract()
        return tag

    #处理不是页面的网址
    def dealWtihNonPage(self,response,url):
        xpath_str='//div[@class="span8 column_container"]/div[@class="td_mod_wrap td_mod8 "]/div[@class="item-details"]/h3/a/@href'
        pages_arr=response.xpath(xpath_str).extract()
        results=[]
        for new_page_url in pages_arr:
            results.append(scrapy.Request(new_page_url,callback=self.parse,dont_filter=False))
        prevoius_page_url=self.getPrevoiuPageUrl(response)
        if prevoius_page_url:
            results.append(scrapy.Request(new_page_url,callback=self.parse,dont_filter=True))
        return results


     #获取前面一页的url
    def getPrevoiuPageUrl(self,response):
        xpath_str='//div[@class="page-nav"]/a[not(@class)]/@href'
        previousUrlsPath=response.xpath(xpath_str).extract()
        if len(previousUrlsPath):
            page_url_str=previousUrlsPath[0]
            search_result=re.search(self.previous_page_pat,page_url_str)
            if search_result:
                print "privious page's url is %s " %search_result.group(1)
                return search_result.group(1)
        return None

    #提取当前页面的文件夹路径
    def extractBaseUrl(self,url):
        if None==url:
            return None
        matchResult=re.match(self.base_url_pat,url)
        if matchResult:
            return matchResult.group(1)
        return None
