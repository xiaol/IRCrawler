#coding=utf-8
from news_spider_version2.items import NewsItem, PartialNewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils
from news_spider_version2.spiders.utils.MongoUtils import MongoUtils


__author__ = 'galois'

import scrapy
import re

import HTMLParser
from scrapy.utils.url import canonicalize_url
import hashlib



class DapentiSpider(scrapy.Spider):

    name='dapentiSpider'
    allowed_domains=['www.dapenti.com']

    start_urls=['http://www.dapenti.com/blog/blog.asp?name=agile',
                'http://www.dapenti.com/blog/blog.asp?subjectid=2&name=xilei',
               ]
    # start_urls=['http://www.dapenti.com/blog/more.asp?name=xilei&id=24479']

    root_class='36度'
    #一级分类下面的频道
    default_channel='同步喜好'
     #源网站的名称
    sourceSiteName='喷嚏网'

    default_tag='懂生活'

    tag_map={
        'agile':'懂生活',
        'xilei':'有腔调',
    }

    page_url_pattern=re.compile(r'^http://www.dapenti.com/blog/more(.*?)id=\d+')
    non_page_url_pattern=re.compile(r'^http://www.dapenti.com/blog')

    time_pat=re.compile(r'</a>\s*?@\s*([\d\. ,:]+\w+)\s*?</div>')

    main_text_pat=re.compile(r'<DIV (?:style=".*?"|class=oblog_text) align=left>(.*?)</DIV>',re.DOTALL)

    content_pat=re.compile(r'<span style="font-size: 14px;">.*?</span>|<P>.*?</P>|<(?:img|IMG)(?: .*?)? src=".*?"(?: .*?)?>',re.DOTALL)
    img_pat=re.compile(r'<(?:img|IMG)(?: .*?)? src="(.*?)"(?: .*?)?>',re.DOTALL)
    para_pat=re.compile(r'<span style="font-size: 14px;">(.*?)</span>|<P>(.*?)</P>',re.DOTALL)

    previous_page_pat=re.compile(ur'<a href="([\w:/\d\.]+)"(?: [^<>]+?)?>></a>')

    html_parser = HTMLParser.HTMLParser()
    edit_tag_pat=re.compile(r'\?name=(.*?)&')
    base_url='http://www.dapenti.com/blog/'
    digit_pat=re.compile(r'\d+')
    update_time_pat=re.compile(r'<DIV align=right><SPAN(?: .*?)?>(.*?)</SPAN></DIV>')

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
        fp = hashlib.sha1()
        fp.update(item['sourceUrl'])
        return fp.hexdigest()

    def extractTitle(self,response):
        xpath_str='//title/text()'
        titleStr=response.xpath(xpath_str).extract()[0]
        title=titleStr.split('--')[1]
        return title

    def extractTime(self,response):
        body=response._get_body()
        search_result=re.search(self.update_time_pat,body)
        if search_result:
            raw_time_str=search_result.group(1)
            time=self.formatTimeStr(raw_time_str)
            return time
        return CrawlerUtils.getDefaultTimeStr()

    def formatTimeStr(self,raw_time_str):
        digit_arr=re.findall(self.digit_pat,raw_time_str)
        i=0
        time_arr=[]
        for digit in digit_arr:
            if len(digit)<2:
                time_arr.append('0')
            time_arr.append(digit)
            if i<2:
                time_arr.append('-')
            elif i==2:
                time_arr.append(' ')
            elif i<5:
                time_arr.append(':')
            i=i+1
        time=''.join(time_arr)
        return time


    def extractRootClass(self,response):
        return self.root_class

    def extractChannel(self,response,item):
        return self.default_channel

    def extractContent(self,response):
        body=response._get_body()
        search_result=re.search(self.main_text_pat,body)
        if search_result:
            rawContent=search_result.group(1)
            rawContent=unicode(rawContent,'gbk').encode()
            return CrawlerUtils.extractContent(rawContent,self.content_pat,self.img_pat,self.para_pat)
        return None


    def extractImgUrl(self,response):
        body=response._get_body()
        search_result=re.search(self.main_text_pat,body)
        if search_result:
            rawContent=search_result.group(1)
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
        tag.append(self.default_tag)
        return tag
    #获取文章的tag信息
    def extractEditTag(self,response):
        url=response._get_url()
        searchResult=re.search(self.edit_tag_pat,url)
        if searchResult:
            tag_key=searchResult.group(1)
            if tag_key in self.tag_map:
                return self.tag_map[tag_key]
        return self.default_tag

    #处理不是页面的网址
    def dealWithNonPage(self,response,url):
        xpath_str='//div[@align="left"]/ul/li/a/@href'
        pages_arr=response.xpath(xpath_str).extract()
        request_items=[]
        for elem in pages_arr:
            elem=self.base_url+elem
            request_items.append(scrapy.Request(elem,callback=self.parse,dont_filter=False))
        non_page_results=[]
        non_page_url=self.getPrevoiuPageUrl(response)
        if non_page_url:
            non_page_results.append(scrapy.Request(non_page_url,callback=self.parse,dont_filter=False))
        return non_page_results,request_items


     #获取前面一页的url
    def getPrevoiuPageUrl(self,response):
        xpath_str='//div[@class="paginator"]/span[@class="next"]/link/@href'
        previousUrlsPath=response.xpath(xpath_str).extract()
        if len(previousUrlsPath):
            html_parser=HTMLParser.HTMLParser()
            page_url_str=html_parser.unescape(previousUrlsPath[0])
            return page_url_str
        return None



if __name__=='__main__':
    # some_interface='http://jandan.duoshuo.com/api/threads/listPosts.json?thread_key=comment-2650694&url=http%3A%2F%2Fjandan.net%2Fooxx%2Fpage-1301%26yid%3Dcomment-2650694&image=http%3A%2F%2Fww1.sinaimg.cn%2Fmw600%2Fa00dfa2agw1enxg54qbbfj20n40x6755.jpg&require=site%2Cvisitor%2Cnonce%2CserverTime%2Clang&site_ims=1420356603&lang_ims=1420356603&v=140327'
    # print "the interface is %s"%some_interface
    # html_parser=HTMLParser.HTMLParser()
    # print "the unscaped is %s " %html_parser.unescape(some_interface)
    print "Hello world"
