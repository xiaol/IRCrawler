__author__ = 'yangjiwen'
#coding=utf-8
import json
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils
from news_spider_version2.items import GoogleNewsItem, PartialNewsItem,NewsItem
from news_spider_version2.spiders.utils.MongoUtils import MongoUtils

import scrapy
import re
import time

import HTMLParser


class NeteasePhotoSpider(scrapy.Spider):
    name='NeteasePhotoNews'
    allowed_domains=['news.163.com']

    start_urls=['http://pic.news.163.com/photocenter/api/list/0001/00AN0001,00AO0001,00AP0001/0/10/cacheMoreData.json'
                ]
                # ,'http://pic.news.163.com/photocenter/api/list/0001/00AN0001,00AO0001,00AP0001/10/10/cacheMoreData.json'
                # ,'http://pic.news.163.com/photocenter/api/list/0001/00AN0001,00AO0001,00AP0001/20/10/cacheMoreData.json'



    # start_urls=['http://www.pingwest.com/nexus-9-keyboard-folio-review/']
    # start_urls=['http://www.pingwest.com/10-things-you-need-know-about-windows-10/']
    # start_urls=['http://www.alibuybuy.com/posts/category/collection']
    # start_urls=['http://news.163.com/photoview/00AO0001/87877.html']
    # start_urls=['http://news.163.com/photoview/00AP0001/87852.html']
    # start_urls=['http://news.163.com/photoview/00AP0001/87816.html']


    root_class='40度'
    #一级分类下面的频道
    default_channel='国内/国际/社会'
     #源网站的名称
    sourceSiteName='网易新闻图片'

    channel_pat=re.compile(r'http://news\.163\.com/photoview/(.*?)/.*?html')
    url_pattern=re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    page_url_pattern=re.compile(r'^http://pic\.news\.163\.com/photocenter/api/.*?$')

    total_pages_pattern=re.compile(r'<span class="page-ch">.*?(\d+).*?</span>')
    page_lists_pat=re.compile(r'<a href="(.*?)" class="page-en">\d+</a>')


    title_pat1=re.compile(r'<h1 class="title">(.+?)</h1>')

    tag_pat=re.compile(r'<a target="_blank" href=".+?">(.+?)</a>')

    time_pat=re.compile(r'<span>([\d\-:\s]*?)</span>',re.DOTALL)
    digital_pat=re.compile(r'\d+')

    content_pat=re.compile(r'<p.*?</p>',re.DOTALL)
    img_pat=re.compile(r'<img.*?src="(.*?)".*?>')
    para_pat=re.compile(r'<p.*?>(.*?)</p>')

    previous_page_pat=re.compile(r'<a\s*?href="(http://www\.alibuybuy\.com[^>^<]*?)"\s*?class="next">')
    nonpage_url_pat=re.compile(r'<a\s*?href="(http://www\.alibuybuy\.com.*?\.html)".*?><img')
    # http://www.lensmagazine.com.cn/category/reporting/focus/page/4
    end_content_str='Mtime时光网专稿 未经许可不得转载'
    json_pat=re.compile(r'cacheMoreData\((.*)\)')
    json_list_pat=re.compile(r'{.*?}')
    imgWalljson_pat=re.compile('"list": \[(.*?)\]',re.DOTALL)
    imgWalljson_list_pat=re.compile(r'{.*?"newsurl".*?}',re.DOTALL)


    # http://tu.duowan.com/g/01/82/e7.html
    html_parser = HTMLParser.HTMLParser()
    channel_map={'00AN0001':'国内','00AO0001':'国际','00AP0001':'社会'
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
                return False
            return True



    def dealWithPage(self,response,url):
        # item 的唯一标识 用源网址

        item=GoogleNewsItem()
        item['sourceUrl']=url
        item['_id']=self.generateItemId(item)
        item['root_class']=self.extractRootClass(response)
        item['channel']=self.extractChannel(response,item) #社会 国内 国际
        item['updateTime']=None
        item['createTime']=self.extractcreateTime(response)
        item['title']=None
        item['content']=None
        item['imgUrls']=None
        item['sourceSiteName']=self.extractSourceSiteName(response,item)
        item['relate']=self.extractrelate(response)
        item['originsourceSiteName']=self.extractoriginsourceSiteName(response)
        item['imgWall']=self.extractimgWall(response)
        item['tag']=self.extractTag(response)
        dict_obj=MongoUtils.findPartialItemById(item['_id'])
        item.cloneInfoFromDict(dict_obj)
        # item.printSelf()
        return item



    #源网站的名称
    # sourceSiteName=scrapy.Field()
    # relate=scrapy.Field()
    # originsourceSiteName=scrapy.Field()
    # imgWall=scrapy.Field()
    # tag


    def generateItemId(self,item):
        return item['sourceUrl']

    def extractTitle(self,response):
        raw_title_str=response.xpath('//article[@class="post article"]').extract()[0]
        searchResult1=re.search(self.title_pat1,raw_title_str)
        # searchResult2=re.search(self.title_pat2,raw_title_str)
        # title=searchResult1+searchResult2
        if searchResult1:
            title=searchResult1.group(1)
            # title=searchResult1.group(1)
            title=CrawlerUtils.removeUnwantedTag(title)

            return title
        return None
    def extractcreateTime(self,response):
        return CrawlerUtils.getDefaultTimeStr()


    def extractTime(self,response):

        raw_time_str=response.xpath('//div[@class="postmeta"]').extract()
        print "raw,%s"%raw_time_str
        searchResult=re.search(self.time_pat,str(raw_time_str))
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
        searchResult=re.search(self.channel_pat,item['sourceUrl'])
        if searchResult:
            channelkey=searchResult.group(1)
        #     return self.default_channel
            channel=self.channel_map[channelkey]  #item['tag'][0].lower().encode('utf-8')
            if channel:
                print "channel is %s " %channel
                return channel
        return self.default_channel


    def extractrelate(self,response):

        return None

    def extractContent(self,response):
        rawContent=response.xpath('//div[@class="article-content"]').extract()[0]
        if not len(rawContent):
            return None
        listInfos=[]
        print "rawcontent,%s" %rawContent
        find_result=re.findall(self.content_pat,rawContent)
        print "rawcontent %s" %find_result
        for line in find_result:
            print "line,%s"%line
            imgSearch=re.findall(self.img_pat,line)
            if imgSearch:
                for img in imgSearch:
                    # img=re.search(self.img_pat,img)
                    listInfos.append({'img':img})
                    print "img is %s" %img

            txtSearch=re.search(self.para_pat,line)
            # txtSearch=rawContent.xpath('/div/text()')
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
        rawContent=response.xpath('//div[@class="article-content"]').extract()
        if not len(rawContent):
            return None
        for line in re.findall(self.content_pat,rawContent[0]):
            imgSearch=re.search(self.img_pat,line)
            if imgSearch:
                print "imgsearch,%s"%imgSearch
                return imgSearch.group(1)
        return None

    def extractDesc(self,response):
        rawContent=response.xpath('//div[@class="newsnote"]/text()').extract()

        if rawContent:
            return rawContent

        return None

    def extractSourceSiteName(self,response,item):
        searchResult=re.search(self.channel_pat,item['sourceUrl'])
        if searchResult:
            channelkey=searchResult.group(1)
        #     return self.default_channel
            channel=self.channel_map[channelkey]  #item['tag'][0].lower().encode('utf-8')
            if channel:
                print "channel is %s " %channel
                return "网易"+channel+"新闻"

        return self.sourceSiteName

    def extractoriginsourceSiteName(self,response):

        return self.sourceSiteName


    def extractrelate(self,response):

        return None

    def extractimgWall(self,response):
        imgWall=response.xpath('//textarea[@name="gallery-data"]').extract()[0]
        print "imgwall,%s"%imgWall
        listInfos=[]
        imgWalljsonSearch=re.search(self.imgWalljson_pat,imgWall)
        if imgWalljsonSearch:
            print "imgWalljsonSearch,%s"%imgWalljsonSearch.group(1)

        imgWalljson_list=re.findall(self.imgWalljson_list_pat,imgWalljsonSearch.group(1))
        for imgWalljson_elem in imgWalljson_list:
            print "imgWalljson_elem,%s"%imgWalljson_elem

                    # json_elem=json_elem.decode('utf-8')
            dict_obj=json.loads(imgWalljson_elem)
            listInfos.append({'img':dict_obj['img'],'note':dict_obj['note']})
        return listInfos






    #获取文章的tag信息
    def extractTag(self,response):
        tag=response.xpath('//div[@class="tag"]/a/text()').extract()
        print "tag,%s"%tag
        return tag


    #处理不是页面的网址
    def dealWtihNonPage(self,response,url):
        # pages_arr=response.xpath('//div[@id="body"]/div[@id="content"]/div/div[@class="column"]/div[@class="post"]/h2/a/@href').extract()
        try:
            print "response.body,%s"%response.body
            jsonSearch=re.search(self.json_pat,response.body)
            request_items=[]
            if jsonSearch:
                print "jsonSearch,%s"%jsonSearch.group(1)
                json_list=re.findall(self.json_list_pat,jsonSearch.group(1))
                for json_elem in json_list:
                    print "json_elem,%s"%json_elem
                    # json_elem=json_elem.decode('utf-8')
                    dict_obj=json.loads(json_elem)
                    partial_item=self.generatePartialItem(dict_obj)
                    if partial_item:
                        # partial_page_items.append(partial_item)
                        MongoUtils.savePartialItem(partial_item)
                        print "souceUrl is %s" %partial_item['sourceUrl']
                        request_items.append(scrapy.Request(partial_item['sourceUrl'],callback=self.parse,dont_filter=False))
            return request_items
        except Exception:
            return None
        return None

    def generatePartialItem(self,dict_obj):
        partial_item=PartialNewsItem()
        partial_item['content']=dict_obj['desc']
        partial_item['description']=dict_obj['desc']
        partial_item['updateTime']=dict_obj['createdate']
        partial_item['sourceUrl']=dict_obj['seturl']
        partial_item['_id']=dict_obj['seturl']
        partial_item['imgUrl']=dict_obj['cover']
        partial_item['title']=dict_obj['setname']

        return partial_item


        # pages_arr=response.xpath('//div[@class="content articles"]').extract()[0]  #/li[@class="box masonry-brick"
        # find_result=re.findall(self.nonpage_url_pat,pages_arr)
        # print "pages_arr,%s" %pages_arr
        # results=[]
        #
        # for new_page_url_raw in find_result:
        #     # searchResult=re.search(self.nonpage_url_pat,new_page_url_raw)
        #     if new_page_url_raw:
        #         new_page_url=new_page_url_raw    #.group(1)
        #         print "new_page_url is %s" %new_page_url
        #         results.append(scrapy.Request(new_page_url,callback=self.parse,dont_filter=False))
        # prevoius_page_url=self.getPrevoiuPageUrl(response)
        # print "pevoious_page_url,%s"%prevoius_page_url
        # if prevoius_page_url:
        #     results.append(scrapy.Request(prevoius_page_url,callback=self.parse,dont_filter=True))
        # return results



        # for new_page_url in pages_arr:
        #     results.append(scrapy.Request(new_page_url,callback=self.parse,dont_filter=False))
        # prevoius_page_url=self.getPrevoiuPageUrl(response)
        # if prevoius_page_url:
        #     results.append(scrapy.Request(new_page_url,callback=self.parse,dont_filter=True))
        # return results

# http://t.qianzhan.com//dazahui/p-2.html
     #获取前面一页的url
    def getPrevoiuPageUrl(self,response):
        title_sign=u'下一页'
        xpath_str='//div[@class="wpagenavi"]'.decode('utf8')
        previousUrlsPath=response.xpath(xpath_str).extract()
        print "previousUrlsPath,%s"%previousUrlsPath
        searchResult=re.search(self.previous_page_pat,str(previousUrlsPath))

        # print "hello"
        if searchResult:
            page_url_str=searchResult.group(1)
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
