__author__ = 'yangjiwen'
#coding=utf-8
import json
from news_spider_version2.items import NewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils


import scrapy
import re

import HTMLParser


class LensSubzeroSpider(scrapy.Spider):
    name='LensSubzeroNews'
    allowed_domains=['lensmagazine.com.cn']

    start_urls=['http://jandan.net/tag/wtf','http://jandan.net/tag/sex','http://jandan.net/tag/%E7%88%B7%E6%9C%89%E9%92%B1',
                'http://jandan.net/tag/DIY','http://jandan.net/tag/meme','http://jandan.net/tag/Geek','http://jandan.net/tag/%E5%B0%8F%E8%B4%B4%E5%A3%AB',
                'http://jandan.net/tag/%E7%AC%A8%E8%B4%BC','http://jandan.net/tag/%E7%86%8A%E5%AD%A9%E5%AD%90']

    start_urls=['http://www.lensmagazine.com.cn/category/reporting/focus','http://www.lensmagazine.com.cn/category/reporting/special-topic']

    # start_urls=['http://www.lensmagazine.com.cn/reporting/focus/10174.html']

    # start_urls=['http://www.lensmagazine.com.cn/category/reporting/special-topic']
    # start_urls=['http://www.lensmagazine.com.cn/reporting/special-topic/10703.html']
    # start_urls=['http://www.lensmagazine.com.cn/reporting/focus/3141.html']

    root_class='-40度'
    #一级分类下面的频道
    default_channel='冰封'
     #源网站的名称
    sourceSiteName='Lens'

  
    url_pattern=re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    page_url_pattern=re.compile(r'^http://www\.lensmagazine\.com\.cn/reporting.*?/\d+\.html$')

    total_pages_pattern=re.compile(r'<span class="page-ch">.*?(\d+).*?</span>')
    page_lists_pat=re.compile(r'<a href="(.*?)" class="page-en">\d+</a>')


    title_pat1=re.compile(r'<h4>(.+?)</h4>')
    title_pat2=re.compile(r'<span id="seq">\s*?([\w ( ) /]+)\s*?</span>')

    tag_pat=re.compile(r'<a target="_blank" href=".+?">(.+?)</a>')

    time_pat=re.compile(r'<li>([\d\. ,:]+)</li>')
    digital_pat=re.compile(r'\d+')

    content_pat=re.compile(r'<p>.*?\s*?</p>',re.DOTALL)
    # img_pat=re.compile(r'<img\s*?class=".+?"\s*?alt=".*?"\s*?src="(.*?)"\s*?width="\d+"\s*?height="\d+">')
    img_pat=re.compile(r'<img.*?src="(http://www\.lensmagazine\.com\.cn.*?\.jpg)".*?>')
    para_pat=re.compile(r'<p>(.*?)\s*?</p>',re.DOTALL)

    previous_page_pat=re.compile(r'<a href="(.*?)">»</a>')
    nonpage_url_pat=re.compile(r'<a class="wb-numbers" title=".*?"\s*?href="(http://www.lensmagazine.com.cn/category/reporting/focus.*?)">')
    # http://www.lensmagazine.com.cn/category/reporting/focus/page/4
    end_content_str='以上图文只是杂志上很小的一部分……'


    # http://tu.duowan.com/g/01/82/e7.html
    html_parser = HTMLParser.HTMLParser()
    channel_map={'wtf':'冷新闻','WTF':'冷新闻','sex':'冷新闻','SEX':'冷新闻','爷有钱':'冷新闻',
       'diy':'冷知识','DIY':'冷知识','MEME':'冷知识','GEEK':'冷知识','meme':'冷知识','geek':'冷知识','小贴士':'冷知识',
        '笨贼':'冷幽默','熊孩子':'冷幽默'
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
        raw_title_str=response.xpath('//div[@class="entry"]').extract()[0]
        searchResult1=re.search(self.title_pat1,raw_title_str)
        # searchResult2=re.search(self.title_pat2,raw_title_str)
        # title=searchResult1+searchResult2
        if searchResult1:
            title=searchResult1.group(1)
            # title=searchResult1.group(1)
            return title
        return None

    def extractTime(self,response):
        raw_time_str=response.xpath('//div[@class="entry"]').extract()[0]
        searchResult=re.search(self.time_pat,raw_time_str)
        if searchResult:
            time=searchResult.group(1)
            return self.formatTime(time)
        return CrawlerUtils.getDefaultTimeStr()
     # 2015-01-07 11:50:09
    def formatTime(self,timeStr):
        digitals=re.findall(self.digital_pat,timeStr)
        resultArr=[]
        i=0
        for digit in digitals:
            if len(digit)<2:
                digit='0'+digit

            resultArr.append(digit)
            if i<1:
                resultArr.append('-')
            i=i+1
        other_time=CrawlerUtils.getDefaultTimeStr()[7:]
        resultArr.append(other_time)
        # resultArr1=''.join(resultArr)
        # print "result %s" %resultArr1
        return ''.join(resultArr)

    def extractRootClass(self,response):
        return self.root_class

    def extractChannel(self,response,item):
        # if item['tag']==None:
        #     return self.default_channel
        # channel=self.channel_map[item['tag'][0].lower().encode('utf-8')]
        # if channel:
        #     print "channel is %s " %channel
        #     return channel
        return self.default_channel

    def extractContent(self,response):
        rawContent=response.xpath('//div[@class="entry"]').extract()
        if not len(rawContent):
            return None
        listInfos=[]

        find_result=re.findall(self.content_pat,rawContent[0])
        print "rawcontent %s" %find_result
        for line in find_result:
            # print "line,%s"%line
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
                        if self.end_content_str in result:
                            break
                        # print "txt is :%s" %result
                        listInfos.append({'txt':result})
        # print  "listInfos,%s" %listInfos
        return CrawlerUtils.make_img_text_pair(listInfos)

    def extractImgUrl(self,response):
        rawContent=response.xpath('//div[@class="entry"]').extract()
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
        # raw_title_str=response.xpath('//div[@class="title"]').extract()[0]
        # searchResult1=re.search(self.title_pat1,raw_title_str)

        return None


    #处理不是页面的网址
    def dealWtihNonPage(self,response,url):
        # pages_arr=response.xpath('//div[@id="body"]/div[@id="content"]/div/div[@class="column"]/div[@class="post"]/h2/a/@href').extract()
        pages_arr=response.xpath('//div[@class="entry"]/h4/a/@href').extract()  #/li[@class="box masonry-brick"

        print "pages_arr,%s" %pages_arr
        results=[]

        for new_page_url in pages_arr:
            print "new_page_url is %s" %new_page_url
            results.append(scrapy.Request(new_page_url,callback=self.parse,dont_filter=False))
        prevoius_page_url=self.getPrevoiuPageUrl(response)
        print "pevoious_page_url,%s"%prevoius_page_url
        if prevoius_page_url:
            results.append(scrapy.Request(prevoius_page_url,callback=self.parse,dont_filter=True))
        return results



        # for new_page_url in pages_arr:
        #     results.append(scrapy.Request(new_page_url,callback=self.parse,dont_filter=False))
        # prevoius_page_url=self.getPrevoiuPageUrl(response)
        # if prevoius_page_url:
        #     results.append(scrapy.Request(new_page_url,callback=self.parse,dont_filter=True))
        # return results


     #获取前面一页的url
    def getPrevoiuPageUrl(self,response):
        title_sign=u'下一页'
        xpath_str='//div[@class="box gra"]/ul/li/a[@title="下一页"]/@href'.decode('utf8')
        previousUrlsPath=response.xpath(xpath_str).extract()
        if len(previousUrlsPath):
            page_url_str=previousUrlsPath[0]
            if page_url_str:
                # print "privious page's url is %s " %page_url_str
                return page_url_str
        return None

    # def parseTotalPages(self,contentStr):
    #     if None==contentStr:
    #         return None
    #     searchResult=re.search(self.total_pages_pattern,contentStr)
    #     if searchResult:
    #         return int(searchResult.group(1))
    #     return None


    # #提取当前页面的文件夹路径
    # def extractBaseUrl(self,url):
    #     if None==url:
    #         return None
    #     index=url.rfind("/")
    #     return url[:index+1]




    def main(self,url):
       urlStr=self.getHtmlContentUnicode(url)
       print urlStr




if __name__=='__main__':
    some_interface='http://jandan.duoshuo.com/api/threads/listPosts.json?thread_key=comment-2650694&url=http%3A%2F%2Fjandan.net%2Fooxx%2Fpage-1301%26yid%3Dcomment-2650694&image=http%3A%2F%2Fww1.sinaimg.cn%2Fmw600%2Fa00dfa2agw1enxg54qbbfj20n40x6755.jpg&require=site%2Cvisitor%2Cnonce%2CserverTime%2Clang&site_ims=1420356603&lang_ims=1420356603&v=140327'
    print "the interface is %s"%some_interface
    html_parser=HTMLParser.HTMLParser()
    print "the unscaped is %s " %html_parser.unescape(some_interface)
