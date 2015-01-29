__author__ = 'yangjiwen'
#coding=utf-8
import json
from news_spider_version2.items import NewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils


import scrapy
import re

import HTMLParser


class LensSubzeroSpider(scrapy.Spider):
    name='NeteaseHeadlineNews'

    allowed_domains=['zhenhua.163.com']

    start_urls=['http://jandan.net/tag/wtf','http://jandan.net/tag/sex','http://jandan.net/tag/%E7%88%B7%E6%9C%89%E9%92%B1',
                'http://jandan.net/tag/DIY','http://jandan.net/tag/meme','http://jandan.net/tag/Geek','http://jandan.net/tag/%E5%B0%8F%E8%B4%B4%E5%A3%AB',
                'http://jandan.net/tag/%E7%AC%A8%E8%B4%BC','http://jandan.net/tag/%E7%86%8A%E5%AD%A9%E5%AD%90']

    start_urls=['http://zhenhua.163.com/special/2014shangtoutiao']

    # start_urls=['http://zhenhua.163.com/special/shangtoutiao2014_mh370']

    # start_urls=['http://zhenhua.163.com/special/shangtoutiao2014_yangweijun/']



    root_class='-40度'
    #一级分类下面的频道
    default_channel='冰封'
     #源网站的名称
    sourceSiteName='网易'


    url_pattern=re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    page_url_pattern=re.compile(r'^http://zhenhua\.163\.com/special/[^0-9]+.*?$')

    total_pages_pattern=re.compile(r'<span class="page-ch">.*?(\d+).*?</span>')
    page_lists_pat=re.compile(r'<a href="(.*?)" class="page-en">\d+</a>')


    title_pat1=re.compile(r'<h3>(.+?)</h3>',re.DOTALL)
    title_pat2=re.compile(r'<span id="seq">\s*?([\w ( ) /]+)\s*?</span>')

    tag_pat=re.compile(r'<a target="_blank" href=".+?">(.+?)</a>')

    time_pat=re.compile(r'<time.*?>(.*?)</time>')
    digital_pat=re.compile(r'\d+')

    content_pat=re.compile(r'<p.*?</p>|<img.*?>|<span>.*?</span>',re.DOTALL)
    content_pat1=re.compile(r'<img\s*?src=".*?"\s*?alt=".*?".*?>')
    content_pat2=re.compile(r'<img\s*?src="(.*?)"\s*?alt="pic">')
    img_pat=re.compile(r'<img\s*?alt=".*?"\s*?src="(.*?)">')
    para_pat1=re.compile(r'<p.*?>\s*?(.*?)\s*?</p>',re.DOTALL)
    para_pat2=re.compile(r'<span>(.*?)</span>',re.DOTALL)
    previous_page_pat=re.compile(r'<a href="(.*?)">»</a>')
    nonpage_url_pat=re.compile(r'<a.*?helink="(.*?)"\s*?hetext="\S+".*?hepos="left">')

    nonpage_url_pat_1=re.compile(r'<a.*?helink=".*?"\s*?hetext="\S+".*?hepos="left">')
    # <a class="sc-cur" href="javascript:;" target="_self" pltype="6" topicid="0001" sid="V9G6428S1" vid="V9GDRSQ3T" coverpic="http://img6.cache.netease.com/cnews/2013/12/30/20131230002308ee611.png" mpfour="http://flv.bn.netease.com/videolib3/1312/30/rLCZc2935/HD/rLCZc2935-mobile.mp4" hename="李侗奎" helink="http://news.163.com/special/coldnewsltk/" hetext="失独者：无法承受的余生>>" helife="他19岁结婚，婚后有了儿子李征。因当时计划生育政策抓的紧，考虑到生下的孩子又是男孩，可以传宗接代，他没有选择再生。后来儿子因病去世，他成为了失独者。时至今日，他仍然无法从丧子之痛中走出来。他说，不久的将来爸爸也会找你的。" hepos="left">

    # http://www.lensmagazine.com.cn/category/reporting/focus/page/4
    end_content_str='上头条往期回顾'


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
        print "hello"
        raw_title_str=response.xpath('//div[@class="inner-right"]/div[@class="title"]').extract()[0]
        # raw_title_str=response.xpath('//div[@class="headerBar"]').extract()[0]
        searchResult1=re.search(self.title_pat1,raw_title_str)

        if searchResult1:
            title=searchResult1.group(1)
            title=title.replace('\n','')
            title=title.replace('\t','')
            title=CrawlerUtils.removeUnwantedTag(title)
            # title=searchResult1.group(1)
            return title
        return None

    def extractTime(self,response):

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
            if i<2:
                resultArr.append('-')
            i=i+1
        other_time=CrawlerUtils.getDefaultTimeStr()[10:]
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

        rawContent1=response.xpath('//div[@class="inner-right"]').extract()

        if not len(rawContent1):
            return None
        listInfos=[]
        find_result1=re.findall(self.content_pat,rawContent1[0])
        # print "find_result %s" %find_result[0][0]

        for line in find_result1:
            print "line,%s"%line
            imgSearch=re.search(self.content_pat2,line)
            if imgSearch:
                listInfos.append({'img':imgSearch.group(1)})
                print "img is %s" %imgSearch.group(1)

            else:

                txtSearch1=re.search(self.para_pat1,line)
                txtSearch2=re.search(self.para_pat2,line)
                if txtSearch1:
                    result=txtSearch1.group(1)
                    result=CrawlerUtils.removeParasedCode(result)
                    result=CrawlerUtils.removeScript(result)
                    result=CrawlerUtils.removeUnwantedTag(result)
                    if (not CrawlerUtils.isAllSpaces(result)) & (not CrawlerUtils.isPagesInfo(result)):
                        result=CrawlerUtils.Q_space+CrawlerUtils.Q_space+result.strip()+'\n\n'
                        if self.end_content_str in result:
                            break
                        print "txt is :%s" %result
                        listInfos.append({'txt':result})
                elif txtSearch2:
                    result=txtSearch2.group(1)
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

        rawContent=response.xpath('//div[@class="inner-right"]').extract()
        if not len(rawContent):
            return None
        for line in re.findall(self.content_pat,rawContent[0]):
            imgSearch=re.search(self.content_pat2,line)
            print "imgsearch,%s"%imgSearch
            if imgSearch:
                print "imgsearch,%s" %imgSearch.group(1)
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


        pages_arr=response.xpath('//ul[@class="accordion"]/li/div[@class="description"]/h2/a/@href').extract()  #/li[@class="box masonry-brick"
        # pages_result=re.findall(self.nonpage_url_pat_1,pages_arr)
        # results=[]
        print "pages_arr,%s" %pages_arr
        results=[]
        for new_page_url in pages_arr:
            # print "new_page_url,%s"%new_page_url
            if new_page_url:
                # new_page_url_1=re.search(self.nonpage_url_pat,new_page_url)
                # new_page_url2=new_page_url_1.group(1)
                # print "new_page_url2,%s"%new_page_url2
                results.append(scrapy.Request(new_page_url,callback=self.parse,dont_filter=False))
        # prevoius_page_url=self.getPrevoiuPageUrl(response)
        # if prevoius_page_url:
        #     results.append(scrapy.Request(new_page_url,callback=self.parse,dont_filter=True))
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
       # print urlStr

#
#
if __name__=='__main__':
    some_interface='http://jandan.duoshuo.com/api/threads/listPosts.json?thread_key=comment-2650694&url=http%3A%2F%2Fjandan.net%2Fooxx%2Fpage-1301%26yid%3Dcomment-2650694&image=http%3A%2F%2Fww1.sinaimg.cn%2Fmw600%2Fa00dfa2agw1enxg54qbbfj20n40x6755.jpg&require=site%2Cvisitor%2Cnonce%2CserverTime%2Clang&site_ims=1420356603&lang_ims=1420356603&v=140327'
    print "the interface is %s"%some_interface
    html_parser=HTMLParser.HTMLParser()
    print "the unscaped is %s " %html_parser.unescape(some_interface)
