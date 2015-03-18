__author__ = 'yangjiwen'
#coding=utf-8
import json
from news_spider_version2.items import NewsItem, GoogleNewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils
from news_spider_version2.spiders.utils.MongoUtils import MongoUtils


import scrapy
import re

import HTMLParser


class GoogleFocusNewsSpider(scrapy.Spider):
    name='GoogleFocusNews'

    # allowed_domains=['news.google.com.hk']

    start_urls=['https://news.google.com.hk/nwshp?hl=zh-CN&tab=wn']

    # start_urls=['file:///Users/yangjiwen/Documents/xiongjun/GoogleNewsHtml/Google_directry2.html']

    # start_urls=['file:///Users/yangjiwen/Documents/xiongjun/GoogleNewsHtml/Google_direcotry2.html']



    # start_urls=['http://www.chinanews.com/gn/2015/03-09/7113590.shtml']
    # start_urls=['http://world.yam.com/post.php?id=3292']
    # start_urls=['http://world.yam.com/post.php?id=3296']

    root_class='40度'
    #一级分类下面的频道
    default_channel='最热门'
     #源网站的名称
    sourceSiteName='谷歌焦点新闻'


    url_pattern=re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    page_url_pattern=re.compile(r'^http://world\.yam\.com/post\.php\?id=\d+?$')

    total_pages_pattern=re.compile(r'<span class="page-ch">.*?(\d+).*?</span>')
    page_lists_pat=re.compile(r'<a href="(.*?)" class="page-en">\d+</a>')


    title_pat1=re.compile(r'<h2>(.+?)</h2>')
    title_pat2=re.compile(r'<span id="seq">\s*?([\w ( ) /]+)\s*?</span>')
    partial_title_pat=re.compile(r'<span class="titletext">(.*?)</span>')

    tag_pat=re.compile(r'<a target="_blank" href=".+?">(.+?)</a>')

    time_pat=re.compile(r'<time.*?>(.*?)</time>')
    digital_pat=re.compile(r'\d+')

    content_pat=re.compile(r'<p>.*?</p>|<img.*?>',re.DOTALL)

    img_pat=re.compile(r'<img\s*?class=".*?"\s*?src="(.*?)"\s*?data-original=".*?"\s*?alt=".*?">')
    para_pat=re.compile(r'<p>(.*?)</p>',re.DOTALL)

    previous_page_pat=re.compile(r'<a href="(.*?)">»</a>')

    nonpage_url_pat=re.compile(r'<h2 class="esc-lead-article-title"><a.*?url="(.*?\.[s]?htm[l]?)"[^>]*?><span class="titletext">')
    # =re.compile(r'<h2 class="esc-lead-article-title"><a.*?url=".*?\.[s]?htm[l]?"[^>]*?><span class="titletext">|<span class="media-strip-item-state"><a.*?url=".*?\.[s]?htm[l]?"[^>]*?><div class="item-image-wrapper">')
    nonpage_url_pat_search=re.compile(r'<h2 class="esc-lead-article-title"><a.*?url="(.*?\.[s]?htm[l]?[^>]*?)"[^>]*?><span class="titletext">|<span class="media-strip-item-state"><a.*?url="(.*?\.[s]?htm[l]?)"[^>]*?><div class="item-image-wrapper">')
    # http://www.lensmagazine.com.cn/category/reporting/focus/page/4

    partial_description_pat=re.compile(r'<div class="esc-lead-snippet-wrapper">(.*?)</div>')

    bottom_page_url_pat=re.compile(r'<span class="media-strip-item-state"><a.*?url="(.*?\.[s]?[htm]?[l]?[^<^>]*?)"[^<^>]*?><div class="item-image-wrapper">')

    middle_page_url_pat=re.compile(r'<div class="esc-secondary-article-title-wrapper"><a.*?url="(.*?\.[s]?htm[l]?[^<^>]*?)"[^<^>]*?><span')

    opinion_page_url_pat=re.compile(ur'<label class="esc-diversity-article-category">观点：</label><a.*?url="(.*?\.[s]?htm[l]?[^<^>]*?)"[^<^>]*?><span')
    deep_report_page_url_pat=re.compile(ur'<label class="esc-diversity-article-category">深入报道：</label><a.*?url="(.*?\.[s]?htm[l]?[^<^>]*?)"[^<^>]*?><span')

    left_page_url_pat=re.compile(r'<div class="esc-thumbnail-wrapper"><div class="esc-thumbnail-state"><div class="esc-thumbnail".*?><a.*?url="(.*?\.[s]?htm[l]?[^<^>]*?)"[^<^>]*?><div')

    end_content_str='以上图文只是杂志上很小的一部分……'
    start_content_str='-本文'

    # http://tu.duowan.com/g/01/82/e7.html
    html_parser = HTMLParser.HTMLParser()
    channel_map={'wtf':'冷新闻','WTF':'冷新闻','sex':'冷新闻','SEX':'冷新闻','爷有钱':'冷新闻',
       'diy':'冷知识','DIY':'冷知识','MEME':'冷知识','GEEK':'冷知识','meme':'冷知识','geek':'冷知识','小贴士':'冷知识',
        '笨贼':'冷幽默','熊孩子':'冷幽默'
    }


    def parse(self,response):


        url=response._get_url()
        if  self.isPage(response,url):
            yield self.dealWithPage(response,url)
        else:
            results=self.dealWtihNonPage(response,url)

            # for result in results:
            #     yield(result)


    def isPage(self,response,url):
        if None==url:
            return False
        if url.endswith(".html") or url.endswith(".shtml") or url.endswith(".htm"):
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

        raw_title_str=response.xpath('//article[@class="mainBox xxx"]/header').extract()[0]
        # raw_title_str=response.xpath('//div[@class="headerBar"]').extract()[0]
        searchResult1=re.search(self.title_pat1,raw_title_str)

        if searchResult1:
            title=searchResult1.group(1)
            # title=searchResult1.group(1)
            return title
        return None

    def extractTime(self,response):
        raw_time_str=response.xpath('//div[@class="headerBar"]').extract()[0]
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
        rawContent=response.xpath('//article[@class="mainBox xxx"]').extract()
        if not len(rawContent):
            return None
        listInfos=[]

        find_result=re.findall(self.content_pat,rawContent[0])
        # print "rawcontent %s" %find_result
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
                        if self.start_content_str in result:
                            return False
                        if self.end_content_str in result:
                            break
                        print "txt is :%s" %result
                        listInfos.append({'txt':result})
        # print  "listInfos,%s" %listInfos
        return CrawlerUtils.make_img_text_pair(listInfos)

    def extractImgUrl(self,response):
        rawContent=response.xpath('//article[@class="mainBox xxx"]').extract()
        if not len(rawContent):
            return None
        for line in re.findall(self.content_pat,rawContent[0]):
            imgSearch=re.search(self.img_pat,line)
            if imgSearch:
                # print "imgsearch,%s" %imgSearch.group(1)
                return imgSearch.group(1)
        return None

    def extractDesc(self,response):
        return None

    def extractSourceSiteName(self,response):
        return self.sourceSiteName

    #获取文章的tag信息
    def extractTag(self,response):
        tag=response.xpath('//div[@class="tabsBox curr"]/a/text()').extract()
        # searchResult1=re.search(self.title_pat1,raw_title_str)
        if tag:
            print "tag,%s"%tag
            return tag
        return None


    #处理不是页面的网址
    def dealWtihNonPage(self,response,url):
        # pages_arr=response.xpath('//div[@id="body"]/div[@id="content"]/div/div[@class="column"]/div[@class="post"]/h2/a/@href').extract()
        pages_arr=response.xpath('//div[@class="section top-stories-section"]/div[@class="section-content"]/div/div/div/div[@class="esc-body"]')  #/li[@class="box masonry-brick"
        for theme_page in pages_arr:
            print "theme_page,%s"%theme_page.extract()
            theme_page=theme_page.extract()
            theme_page_url=re.findall(self.nonpage_url_pat,theme_page)
            print "theme_page_url,%s"%theme_page_url
            partial_item=GoogleNewsItem()
            partial_item['sourceUrl']=theme_page_url[0]
            partial_item['_id']=theme_page_url[0]
            title=re.findall(self.partial_title_pat,theme_page)
            partial_item['title']=title[0]
            print "title,%s"%partial_item['title']

            description=re.findall(self.partial_description_pat,theme_page)
            partial_item['description']=description
            print "description,%s"%partial_item['description']

            partial_item['updateTime']=CrawlerUtils.getDefaultTimeStr()

            related_url=[]
            bottom_page_url=re.findall(self.bottom_page_url_pat,theme_page)
            for new_page_url in bottom_page_url:
                print "new_page_url,%s"%new_page_url
                related_url.append(({'bottom':new_page_url}))

            middle_page_url=re.findall(self.middle_page_url_pat,theme_page)
            for new_page_url in middle_page_url:
                print "new_page_url,%s"%new_page_url
                related_url.append(({'middle':new_page_url}))

            opinion_page_url=re.findall(self.opinion_page_url_pat,theme_page)
            if opinion_page_url:
                for new_page_url in opinion_page_url:
                    print "new_page_url,%s"%new_page_url
                    related_url.append(({'opinion':new_page_url}))

            deep_report_page_url=re.findall(self.deep_report_page_url_pat,theme_page)
            if deep_report_page_url:
                for new_page_url in deep_report_page_url:
                    print "new_page_url,%s"%new_page_url
                    related_url.append(({'deep_report':new_page_url}))

            left_page_url=re.findall(self.left_page_url_pat,theme_page)
            if left_page_url:
                for new_page_url in left_page_url:
                    print "new_page_url,%s"%new_page_url
                    related_url.append(({'left':new_page_url}))

            partial_item['relatedUrl']=related_url
            partial_item['root_class']=self.root_class
            partial_item['channel']=self.default_channel
            partial_item['sourceSiteName']=self.sourceSiteName
            partial_item['imgUrl']=None
            if partial_item:
                MongoUtils.saveGoogleItem(partial_item)





    #处理不是页面的网址
    # def dealWithNonPage(self,response,url):
    #     pages_tags=response.xpath('//div[@class="layout bline"]/div/div[@class="hd"]/h2/text()').extract()
    #     pages_arr=response.xpath('//div[@class="layout bline"]/div/div[@class="bd"]/ul')
    #     partial_page_items=[]
    #     city=self.extractCity(response,url)
    #     request_items=[]
    #     i=0
    #     for elem_dom in pages_arr:
    #         tag=[]
    #         tag.append(pages_tags[i])
    #         elems=elem_dom.xpath('./li')
    #         for elem in elems:
    #             partial_item=self.generatePartialItem(elem,tag,city,url)
    #             if partial_item:
    #                 # partial_page_items.append(partial_item)
    #                 MongoUtils.savePartialItem(partial_item)
    #                 print "souceUrl is %s" %partial_item['sourceUrl']
    #                 request_items.append(scrapy.Request(partial_item['sourceUrl'],callback=self.parse,dont_filter=False))
    #     return request_items

    def generatePartialItem(self,dom_elem,tag,city,parentUrl):
        partial_item=PartialNewsItem()
        partial_item['tag']=tag
        partial_item['city']=city
        print "city is %s" %city


        source_url_arr=dom_elem.xpath('./a/@href').extract()
        if not len(source_url_arr):
            return None
        source_url=source_url_arr[0]
        if  not source_url.startswith('http'):
            baseUrl=self.extractBaseUrl(parentUrl)
            if baseUrl:
                source_url=baseUrl+source_url
        partial_item['sourceUrl']=source_url
        partial_item['_id']=source_url
        partial_item['imgUrl']=dom_elem.xpath('./a/img/@src').extract()[0]
        partial_item['title']=dom_elem.xpath('./div[@class="info"]/h2/a/text()').extract()[0]
        partial_item['description']=dom_elem.xpath('./div[@class="info"]/p/text()').extract()[0]
        return partial_item




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
