#coding=utf-8
from news_spider_version2.items import NewsItem, PartialNewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils
from news_spider_version2.spiders.utils.MongoUtils import MongoUtils


__author__ = 'galois'

import scrapy
import re

import HTMLParser


class CityTencentSpider(scrapy.Spider):
    name='CityTencentSpider'
    allowed_domains=['qq.com']

    start_urls=['http://sh.qq.com/news','http://gd.qq.com/news','http://cd.qq.com/news',
                'http://xian.qq.com/news','http://hn.qq.com/news','http://hb.qq.com/news',
                'http://fj.qq.com/news','http://henan.qq.com/news','http://henan.qq.com/news',
                'http://zj.qq.com/news','http://ln.qq.com/news','http://js.qq.com/news/index.html'
    ]

    # start_urls=['http://sh.qq.com/a/20150209/008426.htm']

    root_class='36度'
    #一级分类下面的频道
    default_channel='城市'
     #源网站的名称
    sourceSiteName='腾讯新闻'
    default_city="上海"

    page_url_pattern=re.compile(r'^http://[\w]+.qq.com/a/\d+/\d+\.[s]?htm[l]?$')

    total_pages_pattern=re.compile(r'<span class="page-ch">.*?(\d+).*?</span>')
    page_lists_pat=re.compile(r'<a href="(.*?)" class="page-en">\d+</a>')

    time_pat=re.compile(r'</a>\s*?@\s*([\d\. ,:]+\w+)\s*?</div>')
    digital_pat=re.compile(r'\d+')

    content_pat=re.compile(r'<p(?: .*?)?>.*?</p>')
    img_pat=re.compile(r'<img(?: .*?)? src="(.*?)"(?: .*?)?>')
    # para_pat=re.compile(r'<p style="(?:TEXT-INDENT|text-indent).*?">(.+?)</p>')
    para_pat=re.compile(r'<p(?: .*?)?>(.+?)</p>')

    previous_page_pat=re.compile(ur'<a href="([\w:/\d\.]+)"(?: [^<>]+?)?>></a>')
    city_str_pat=re.compile(r'http://(\w+)\.')
    base_url_pat=re.compile(r'(http[s]?://[\w\d\.]+)/')

    html_parser = HTMLParser.HTMLParser()
    city_map={'bj':'北京','tj':'天津','sh':'上海',
            'gd':'广东','cd':'四川',
            'cq':'重庆','xian':'陕西','hn':'湖南',
            'hb':'湖北','fj':'福建','henan':'河南',
            'zj':'浙江','ln':'辽宁','js':'江苏',

    }

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
        matchResult=re.match(self.page_url_pattern,url)
        if matchResult:
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
        item['channel']=self.extractChannel(response,item)
        item['_id']=self.generateItemId(item)
        item['city']=self.extractCity(response,url)
        item['description']=self.extractDesc(response)

        item.printSelf()
        return item


    def generateItemId(self,item):
        return item['sourceUrl']

    def extractTitle(self,response):
        xpathStr='//div[@class="main"]/div[@id="C-Main-Article-QQ"]/div/h1/text()'
        title=response.xpath(xpathStr).extract()[0]
        return title

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



    def extractImgUrl(self,response):
        xpathStr='//div[@class="main"]/div[@id="C-Main-Article-QQ"]/div[@id="Cnt-Main-Article-QQ"]'
        rawContent=response.xpath(xpathStr).extract()
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
        tag.append(self.extractCity(response,response._get_url()))
        return tag

    #处理不是页面的网址
    def dealWithNonPage(self,response,url):
        urls=response.xpath('//a[@target="_blank"]/@href').extract()
        url_set=set([])
        for url in urls:
            if re.match(self.page_url_pattern,url):
                url_set.add(url)
        request_items=[]
        for url in url_set:
            request_items.append(scrapy.Request(url,callback=self.parse,dont_filter=False))
        return request_items



    #提取当前页面的文件夹路径
    def extractBaseUrl(self,url):
        if None==url:
            return None
        matchResult=re.match(self.base_url_pat,url)
        if matchResult:
            return matchResult.group(1)
        return None





    def main(self,url):
       urlStr=self.getHtmlContentUnicode(url)
       print urlStr

if __name__=='__main__':
    some_interface='http://jandan.duoshuo.com/api/threads/listPosts.json?thread_key=comment-2650694&url=http%3A%2F%2Fjandan.net%2Fooxx%2Fpage-1301%26yid%3Dcomment-2650694&image=http%3A%2F%2Fww1.sinaimg.cn%2Fmw600%2Fa00dfa2agw1enxg54qbbfj20n40x6755.jpg&require=site%2Cvisitor%2Cnonce%2CserverTime%2Clang&site_ims=1420356603&lang_ims=1420356603&v=140327'
    print "the interface is %s"%some_interface
    html_parser=HTMLParser.HTMLParser()
    print "the unscaped is %s " %html_parser.unescape(some_interface)
