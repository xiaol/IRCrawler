__author__ = 'yangjiwen'
#coding=utf-8
import json
from news_spider_version2.items import NewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils


import scrapy
import re

import HTMLParser


class ChinaDailySpider(scrapy.Spider):
    name='ChinaDailyNews'

    # allowed_domains=['chinadaily.com']
    allowed_domains=['world.chinadaily.com.cn']

    start_urls=['http://www.lensmagazine.com.cn/category/reporting/focus','http://www.lensmagazine.com.cn/category/reporting/special-topic']

    # start_urls=['http://www.lensmagazine.com.cn/reporting/focus/10174.html']

    start_urls=['http://t.qianzhan.com/dazahui/']
    # start_urls=['http://t.qianzhan.com/dazahui/detail/150120-af9e8c99.html']

    start_urls=['http://world.chinadaily.com.cn/node_1072266.htm']
    # start_urls=['http://world.chinadaily.com.cn/2015-03/19/content_19851494.htm']
     

    # start_urls=['http://cnews.chinadaily.com.cn/node_1021007.htm']

    # start_urls=['http://cnews.chinadaily.com.cn/2015-03/19/content_19852097.htm']
    # start_urls=['http://cnews.chinadaily.com.cn/2015-03/19/content_19852961.htm']


    root_class='40度'
    #一级分类下面的频道
    default_channel='最热门'
     #源网站的名称
    sourceSiteName='中国日报'


    url_pattern=re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    page_url_pattern=re.compile(r'^http://world\.chinadaily\.com\.cn/\d.*?$')

    total_pages_pattern=re.compile(r'<span class="page-ch">.*?(\d+).*?</span>')
    page_lists_pat=re.compile(r'<a href="(.*?)" class="page-en">\d+</a>')


    title_pat1=re.compile(r'<h1 id="title">(.+?)</h1>')
    title_pat2=re.compile(r'<span id="seq">\s*?([\w ( ) /]+)\s*?</span>')

    tag_pat=re.compile(r'<a target="_blank" href=".+?">(.+?)</a>')

    time_pat=re.compile(r'<span>(.*?)</span>')



    digital_pat=re.compile(r'\d+')

    content_pat=re.compile(r'<p.*?</p>|<center.*?>.*?</center>',re.DOTALL)
    img_pat=re.compile(r'<img.*?src="(.*?\.jpg)".*?>')
    para_pat=re.compile(r'<p.*?>(.*?)</p>|<center.*?>(.*?)</center>',re.DOTALL)

    previous_page_pat=re.compile(r'<a\s*?href="(.*?)".*?>.*?</a>')
    nonpage_url_pat=re.compile(r'<a href="(.*?\.htm)" target="_blank">')
    # http://www.lensmagazine.com.cn/category/reporting/focus/page/4
    end_content_str='以上图文只是杂志上很小的一部分……'
    imgurlReg=re.compile(r'\.\./\.\./(.*)')


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
            if re.match(self.page_url_pattern,url):
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
        raw_title_str=response.xpath('//div[@class="hid arc"]').extract()[0]
        searchResult1=re.search(self.title_pat1,raw_title_str)
        # searchResult2=re.search(self.title_pat2,raw_title_str)
        # title=searchResult1+searchResult2
        if searchResult1:
            title=searchResult1.group(1)
            # title=searchResult1.group(1)
            title=CrawlerUtils.removeUnwantedTag(title)
            return title
        return None

    def extractTime(self,response):
        raw_time_str=response.xpath('//div[@class="hid arc"]/div[@class="arcBar"]/div[@class="arcform"]').extract()[0]
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
            if i==3 and timeStr.endswith('pm'):
                hour=int(digit)+12
                digit=str(hour)
            resultArr.append(digit)
            if i<2:
                resultArr.append('-')
            elif i==2:
                resultArr.append(' ')
            elif i<5:
                resultArr.append(':')
            i=i+1
        # second=CrawlerUtils.getDefaultTimeStr().split(':')[-1]
        # resultArr.append(second)
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
        rawContent=response.xpath('//div[@id="Zoom"]').extract()
        if not len(rawContent):
            return None
        listInfos=[]

        find_result=re.findall(self.content_pat,rawContent[0])
        print "rawcontent %s" %find_result
        for line in find_result:
            print "line,%s"%line
            imgSearch=re.search(self.img_pat,line)
            if imgSearch:
                imgSearch=imgSearch.group(1)
                imgSearch=re.search(self.imgurlReg,imgSearch)
                imgSearch=imgSearch.group(1)
                imgSearch='http://world.chinadaily.com.cn/'+imgSearch
                listInfos.append({'img':imgSearch})
                print "img is %s" %imgSearch
            else:
                txtSearch=re.search(self.para_pat,line)
                if txtSearch:
                    result=txtSearch.group()
                    result=CrawlerUtils.removeParasedCode(result)
                    result=CrawlerUtils.removeScript(result)
                    result=CrawlerUtils.removeUnwantedTag(result)
                    if (not CrawlerUtils.isAllSpaces(result)) & (not CrawlerUtils.isPagesInfo(result)):
                        result=CrawlerUtils.Q_space+CrawlerUtils.Q_space+result.strip()+'\n\n'
                        if self.end_content_str in result:
                            break
                        print "txt is :%s" %result
                        listInfos.append({'txt':result})
        # print  "listInfos,%s" %listInfos
        return CrawlerUtils.make_img_text_pair(listInfos)

    def extractImgUrl(self,response):
        rawContent=response.xpath('//div[@id="Zoom"]').extract()
        if not len(rawContent):
            return None
        for line in re.findall(self.content_pat,rawContent[0]):
            imgSearch=re.search(self.img_pat,line)
            if imgSearch:

                imgSearch=imgSearch.group(1)
                imgSearch=re.search(self.imgurlReg,imgSearch)
                imgSearch=imgSearch.group(1)
                imgSearch='http://world.chinadaily.com.cn/'+imgSearch
                print "imgsearch,%s"%imgSearch
                return imgSearch
        return None

    def extractDesc(self,response):
        return None

    def extractSourceSiteName(self,response):
        return self.sourceSiteName

    #获取文章的tag信息
    def extractTag(self,response):
        tag=response.xpath('//div[@class="tags"]/div[@class="fl"]/a/text()').extract()
        print "tag,%s"%tag
        return tag


    #处理不是页面的网址
    def dealWtihNonPage(self,response,url):
        # pages_arr=response.xpath('//div[@id="body"]/div[@id="content"]/div/div[@class="column"]/div[@class="post"]/h2/a/@href').extract()
        pages_arr=response.xpath('//div[@class="hid"]/div[@class="tw3"]/div[@class="txt1"]/h3[@class="bt1"]').extract()  #/li[@class="box masonry-brick"
        print "pages_arr,%s" %pages_arr
        results=[]


        for new_page_url_raw in pages_arr:

            # find_result=re.findall(self.nonpage_url_pat,pages_arr)
            searchResult=re.search(self.nonpage_url_pat,new_page_url_raw)
            if searchResult:
                new_page_url=searchResult.group(1)
                new_page_url='http://world.chinadaily.com.cn/'+new_page_url
                print "new_page_url is %s" %new_page_url
                results.append(scrapy.Request(new_page_url,callback=self.parse,dont_filter=False))

            # prevoius_page_url=self.getPrevoiuPageUrl(response)
            # print "pevoious_page_url,%s"%prevoius_page_url
            # if prevoius_page_url:
            #     results.append(scrapy.Request(prevoius_page_url,callback=self.parse,dont_filter=True))
        return results








# http://t.qianzhan.com//dazahui/p-2.html
     #获取前面一页的url
    def getPrevoiuPageUrl(self,response):
        # title_sign=u'下一页'
        xpath_str='//div[@class="main"]/div[@class="feed-more"]'.decode('utf8')
        previousUrlsPath=response.xpath(xpath_str).extract()
        searchResult=re.search(self.previous_page_pat,str(previousUrlsPath))
        # print "hello"
        if searchResult:
            page_url_str=searchResult.group(1)
            if page_url_str:
                page_url_str="http://t.qianzhan.com/"+page_url_str
                print "privious page's url is %s " %page_url_str
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