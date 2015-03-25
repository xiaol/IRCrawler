#coding=utf-8
import json
from news_spider_version2.items import NewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils


__author__ = 'galois'

import scrapy
import re
import HTMLParser


class HaiwaiSpider(scrapy.Spider):
    name='HaiwaiSpider'
    allowed_domains=['world.haiwainet.cn']

    start_urls=['http://world.haiwainet.cn/456832/']

    root_class='0度'
    #一级分类下面的频道
    default_channel='冷新闻'
     #源网站的名称
    sourceSiteName='海外网'


    page_url_pattern=re.compile(r'^http://world.haiwainet.cn/n/\d+/\d+/[\d\w-]+\.htm[l]?')
    non_page_url_pattern=re.compile(r'http://world.haiwainet.cn/456832/')

    time_pat=re.compile(r'</a>\s*?@\s*([\d\. ,:]+\w+)\s*?</div>')
    digital_pat=re.compile(r'\d+')

    content_pat=re.compile(r'<p>.*?</p>')
    img_pat=re.compile(r'<p>\s*?<img(?: .*?)? src="(.*?)"(?: .*?)?></p>')
    para_pat=re.compile(r'<p>([^<>]+?)</p>')

    previous_page_pat=re.compile(r'<a href="(.*?)">»</a>')


    html_parser = HTMLParser.HTMLParser()


    def parse(self,response):

        url=response._get_url()
        isPageResult=self.isPage(response,url)
        if None==isPageResult:
            return

        if isPageResult:
            yield self.dealWithPage(response,url)
        else:
            results=self.dealWtihNonPage(response,url)
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
        item['description']=self.extractDesc(response)
        item['channel']=self.extractChannel(response,item)
        item['_id']=self.generateItemId(item)

        item.printSelf()
        return item


    def generateItemId(self,item):
        return item['sourceUrl']

    def extractTitle(self,response):
        xpath_str='//h1[@id="atitle"]/text()'
        title=response.xpath(xpath_str).extract()[0]
        return title

    def extractTime(self,response):
        xpath_str='//article/div[@class="article-info"]/span[@id="acreatedtime"]/text()'
        raw_time_str=response.xpath(xpath_str).extract()[0]
        time=raw_time_str;
        return time;

    def extractRootClass(self,response):
        return self.root_class

    def extractChannel(self,response,item):
        return self.default_channel

    def extractContent(self,response):
        xpath_str='//div[@id="abody"]'
        rawContent=response.xpath(xpath_str).extract()
        if not len(rawContent):
            return None
        listInfos=[]

        for line in re.findall(self.content_pat,rawContent[0]):
            imgSearch=re.search(self.img_pat,line)
            if imgSearch:
                listInfos.append({'img':imgSearch.group(1)})
                # print "img is %s" %imgSearch.group(1)
            else:
                txtSearch=re.search(self.para_pat,line)
                if txtSearch:
                    result=txtSearch.group(1)
                    result=CrawlerUtils.removeParasedCode(result)
                    result=CrawlerUtils.removeScript(result)
                    result=CrawlerUtils.removeUnwantedTag(result)
                    if (not CrawlerUtils.isAllSpaces(result)) & (not CrawlerUtils.isPagesInfo(result)):
                        result=CrawlerUtils.Q_space+CrawlerUtils.Q_space+result.strip()+'\n\n'
                        # print "txt is :%s" %result
                        listInfos.append({'txt':result})
        return CrawlerUtils.make_img_text_pair(listInfos)

    def extractImgUrl(self,response):
        xpath_str='//div[@id="abody"]'
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
        tag=response.xpath('//div[@id="content"]/h3/a[@rel="tag"]/text()').extract()
        return tag

    #处理不是页面的网址
    def dealWtihNonPage(self,response,url):
        xpath_str='//div[@class="list-box"]/ul/li/div[@class="pic"]/a/@href'
        pages_arr=response.xpath(xpath_str).extract()
        results=[]
        for new_page_url in pages_arr:
            print "new page url is %s" %new_page_url
            results.append(scrapy.Request(new_page_url,callback=self.parse,dont_filter=False))
        prevoius_page_url=self.getPrevoiuPageUrl(response)
        if prevoius_page_url:
            results.append(scrapy.Request(new_page_url,callback=self.parse,dont_filter=True))
        return results


     #获取前面一页的url
    def getPrevoiuPageUrl(self,response):
        previousUrlsPath=response.xpath('//div[@class="wp-pagenavi"]').extract()
        if len(previousUrlsPath):
            page_url_str=previousUrlsPath[0]
            search_result=re.search(self.previous_page_pat,page_url_str)
            if search_result:
                print "privious page's url is %s " %search_result.group(1)
                return search_result.group(1)
        return None

    # def parseTotalPages(self,contentStr):
    #     if None==contentStr:
    #         return None
    #     searchResult=re.search(self.total_pages_pattern,contentStr)
    #     if searchResult:
    #         return int(searchResult.group(1))
    #     return None


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
