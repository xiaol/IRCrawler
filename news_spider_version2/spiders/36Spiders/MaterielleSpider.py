#coding=utf-8
from news_spider_version2.items import NewsItem, PartialNewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils


__author__ = 'galois'

import scrapy
import re

import HTMLParser


class MateriellerSpider(scrapy.Spider):
    name='materiellerSpider'
    allowed_domains=['materielle.cn']

    start_urls=['http://materielle.cn/fashion.aspx?Class_id=4',
                'http://materielle.cn/fashion.aspx?Class_id=2',
                'http://materielle.cn/fashion.aspx?Class_id=7',
                'http://materielle.cn/fashion.aspx?Class_id=3']
    start_urls=['http://materielle.cn/fashion1.aspx?Class_id=2&Class_page=419']

    base_url='http://materielle.cn/'

    root_class='36度'
    #一级分类下面的频道
    default_channel='同步喜好'
     #源网站的名称
    sourceSiteName='物质生活'

    default_tag='懂生活'

    tag_map={
        "travel":"懂生活",
        "fashion":"拗造型",
        "beauty":"拗造型",
        "culture":"拗造型",
    }

    page_url_pattern=re.compile(r'^http://materielle\.cn/.*?\.aspx\?Class_id=\d+&Class_page=\d+')
    non_page_url_pattern=re.compile(r'^http://materielle\.cn/.*?\.aspx\?Class_id=\d+?')

    digit_pat=re.compile(r'\d+')
    time_pat=re.compile(r'</a>\s*?@\s*([\d\. ,:]+\w+)\s*?</div>')

    content_pat=re.compile(r'<p>\s*?.+?\s*?</p>',re.DOTALL)
    img_pat=re.compile(r'<img(?: .*?)? src="(.*?)"(?: .*?)?>',re.DOTALL)
    para_pat=re.compile(r'<span style=".*?">(.*?)</span>',re.DOTALL)

    # previous_page_pat=re.compile(ur'<a href="([\w:/\d\.]+)"(?: [^<>]+?)?>></a>')

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
            results=self.dealWithNonPage(response,url)
            # for non_page_result in non_page_results:
            #     yield(non_page_result)
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
        xpath_str='//div[@class="fashion_l"]/span[@style]/text()'
        title=response.xpath(xpath_str).extract()[0]
        title=title.strip()
        return title

    def extractTime(self,response):
        xpath_str='//div[@class="fashion_l"]/span[@style]/text()'
        raw_time_arr=response.xpath(xpath_str).extract()
        raw_time_str=raw_time_arr[2]
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
        xpath_str='//div[@class="fashion_l"]'
        rawContent=response.xpath(xpath_str).extract()[0]
        base_url=self.base_url[0:len(self.base_url)-1]
        print "the base_url is %s" %base_url
        return CrawlerUtils.extractContentImgTxtMixture(rawContent,self.content_pat,self.img_pat,self.para_pat,base_url)


    def extractImgUrl(self,response):
        xpath_str='//div[@class="fashion_l"]'
        rawContent=response.xpath(xpath_str).extract()
        if not len(rawContent):
            return None
        for line in re.findall(self.content_pat,rawContent[0]):
            imgSearch=re.search(self.img_pat,line)
            if imgSearch:
                base_url=self.base_url[0:len(self.base_url)-1]
                return base_url+imgSearch.group(1)
        return None

    def extractDesc(self,response):
        return None

    def extractSourceSiteName(self,response):
        return self.sourceSiteName

    #获取文章的tag信息
    def extractTag(self,response):
        tag=[]
        xpath_str='//div[@class="nav_t"]/text()'
        category=response.xpath(xpath_str).extract()[0]
        if category in self.tag_map:
             tag.append(self.tag_map[category])
        else:
            tag.append(self.default_tag)
        return tag

    #处理不是页面的网址
    def dealWithNonPage(self,response,url):
        xpath_str='//div[@class="fashion_l_1"]/div[@class="dis1"]/a/@href'
        pages_arr=response.xpath(xpath_str).extract()
        request_items=[]
        for elem in pages_arr:
            page_url=self.base_url+elem
            print "the page url is %s" %page_url
            request_items.append(scrapy.Request(page_url,callback=self.parse,dont_filter=False))

        # non_page_results=[]
        # non_page_url=self.getPrevoiuPageUrl(response)
        # non_page_results.append(scrapy.Request(non_page_url,callback=self.parse,dont_filter=False))
        return request_items


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
    spider=MateriellerSpider()
    base_url=spider.base_url[0:len(spider.base_url)-1]
    print "the base_url is %s" %base_url
    print "Hello world"
