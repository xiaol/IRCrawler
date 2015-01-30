#coding=utf-8
from news_spider_version2.items import NewsItem, PartialNewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils


__author__ = 'galois'

import scrapy
import re

import HTMLParser


class ViceCnSpider(scrapy.Spider):
    name='viceCnSpider'
    allowed_domains=['www.vice.cn']

    start_urls=['http://www.vice.cn/news',
                'http://www.vice.cn/travel',
                'http://www.vice.cn/fasion',
                'http://www.vice.cn/photo',
                'http://www.vice.cn/noisey',
                'http://www.vice.cn/tag/漫画']
    # start_urls=['http://www.vice.cn/read/shit-happens-20150105']

    base_url="http://www.vice.cn"

    root_class='36度'
    #一级分类下面的频道
    default_channel='同步喜好'
     #源网站的名称
    sourceSiteName='Vice中国'

    default_tag='懂生活'

    tag_map={
        "事儿":"懂生活","旅行":"懂生活",
        "时尚":"拗造型","摄影":"有腔调",
        "NOISEY 音乐":"有腔调","漫画":"玩出范"
    }

    page_url_pattern=re.compile(r'^http://www.vice.cn/read/.*')
    non_page_url_pattern=re.compile(r'^http://www.vice.cn/.*')

    digit_pat=re.compile(r'\d+')
    time_pat=re.compile(r'</a>\s*?@\s*([\d\. ,:]+\w+)\s*?</div>')

    content_pat=re.compile(r'<p>\s*?.+?\s*?</p>')
    img_pat=re.compile(r'<img(?: .*?)? src="(.*?)"(?: .*?)?>')
    para_pat=re.compile(r'<p>\s*?(.+?)\s*?</p>')

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
        item['channel']=self.extractChannel(response,item)
        item['_id']=self.generateItemId(item)
        item['description']=self.extractDesc(response)
        item.printSelf()
        return item


    def generateItemId(self,item):
        return item['sourceUrl']

    def extractTitle(self,response):
        title=response.xpath('//h1[@class="entry-title single-title"]/span/text()').extract()[0]
        return title

    def extractTime(self,response):
        xpath_str='//div[@class="entry-meta"]/span[@class="entry-date"]/text()'
        raw_time_str=response.xpath(xpath_str).extract()[0]
        time=self.formatTime(raw_time_str)
        return time

    def formatTime(self,raw_time):
        i=0
        digit_arr=[]
        for digit in re.findall(self.digit_pat,raw_time):
            print "the %dth digit is %s" %(i,digit)
            if len(digit)<2:
                digit="0"+digit
            digit_arr.append(digit)
            if(i<2):
                digit_arr.append('-')
            i=i+1
        digit_arr.append(' ')
        default_time=CrawlerUtils.getDefaultTimeStr()
        digit_arr.append(default_time.split(' ')[1])
        time=''.join(digit_arr)
        print "the formated time is %s"%time
        return time



    def extractRootClass(self,response):
        return self.root_class

    def extractChannel(self,response,item):
       return self.default_channel

    def extractContent(self,response):
        xpath_str='//div[@class="article_content"]'
        rawContent=response.xpath(xpath_str).extract()[0]
        return CrawlerUtils.extractContent(rawContent,self.content_pat,self.img_pat,self.para_pat)


    def extractImgUrl(self,response):
        xpath_str='//div[@class="article_content"]'
        rawContent=response.xpath(xpath_str).extract()
        if not len(rawContent):
            return None
        for line in re.findall(self.content_pat,rawContent[0]):
            imgSearch=re.search(self.img_pat,line)
            if imgSearch:
                return imgSearch.group(1)
        return None

    def extractDesc(self,response):
        return None

    def extractSourceSiteName(self,response):
        return self.sourceSiteName

    #获取文章的tag信息
    def extractTag(self,response):
        tag=[]
        xpath_str='//div[@class="entry-meta"]/span[@class="entry-category"]/a/text()'
        category=response.xpath(xpath_str).extract()[-1]
        if category in self.tag_map:
             tag.append(self.tag_map[category])
        else:
            tag.append(self.default_tag)
        return tag

    #处理不是页面的网址
    def dealWithNonPage(self,response,url):
        xpath_str='//article[@class]/figure/a/@href'
        pages_arr=response.xpath(xpath_str).extract()
        request_items=[]
        for elem in pages_arr:
            page_url=self.base_url+elem
            request_items.append(scrapy.Request(page_url,callback=self.parse,dont_filter=False))

        non_page_results=[]
        non_page_url=self.getPrevoiuPageUrl(response)
        non_page_results.append(scrapy.Request(non_page_url,callback=self.parse,dont_filter=False))
        return non_page_results,request_items


    #获取前面一页的url
    def getPrevoiuPageUrl(self,response):
        xpath_str='//div[@class="pagination"]/ul/li/a[@class="next page-numbers"]/@href'
        previousUrlsPath=response.xpath(xpath_str).extract()
        if len(previousUrlsPath):
            html_parser=HTMLParser.HTMLParser()
            page_url_str=html_parser.unescape(previousUrlsPath[0])
            return self.base_url+page_url_str
        return None


if __name__=='__main__':
    # some_interface='http://jandan.duoshuo.com/api/threads/listPosts.json?thread_key=comment-2650694&url=http%3A%2F%2Fjandan.net%2Fooxx%2Fpage-1301%26yid%3Dcomment-2650694&image=http%3A%2F%2Fww1.sinaimg.cn%2Fmw600%2Fa00dfa2agw1enxg54qbbfj20n40x6755.jpg&require=site%2Cvisitor%2Cnonce%2CserverTime%2Clang&site_ims=1420356603&lang_ims=1420356603&v=140327'
    # print "the interface is %s"%some_interface
    # html_parser=HTMLParser.HTMLParser()
    # print "the unscaped is %s " %html_parser.unescape(some_interface)
    print "Hello world"
