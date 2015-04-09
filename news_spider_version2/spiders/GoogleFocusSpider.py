__author__ = 'yangjiwen'
#coding=utf-8
import json
from news_spider_version2.items import NewsItem, GoogleNewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils
from news_spider_version2.spiders.utils.MongoUtils import MongoUtils
import datetime
# import urlparse
# import HTMLParser
# import urllib2
# import charade
# import jpype



import scrapy
import re

import HTMLParser
#
# InputSource        = jpype.JClass('org.xml.sax.InputSource')
# StringReader       = jpype.JClass('java.io.StringReader')
# HTMLHighlighter    = jpype.JClass('de.l3s.boilerpipe.sax.HTMLHighlighter')
# BoilerpipeSAXInput = jpype.JClass('de.l3s.boilerpipe.sax.BoilerpipeSAXInput')




class GoogleFocusNewsSpider(scrapy.Spider):
    name='GoogleFocusNews'

    not_allowed_domains=['cn.china.cn/']
    # allowed_domains=['news.google.com.hk']

    start_urls=['https://news.google.com.hk/nwshp?hl=zh-CN&tab=wn']

    # start_urls=['file:///Users/yangjiwen/Documents/xiongjun/GoogleNewsHtml/Google_directry2.html']

    # start_urls=['file:///Users/yangjiwen/Documents/xiongjun/GoogleNewsHtml/Google_direcotry2.html']
    start_urls=['file:///Users/yangjiwen/Documents/xiongjun/GoogleNewsHtml/Google_direcotry7.html']


    # start_urls=['http://www.chinanews.com/gn/2015/03-09/7113590.shtml']
    # start_urls=['http://world.yam.com/post.php?id=3292']
    # start_urls=['http://world.yam.com/post.php?id=3296']

    # start_urls=['http://www.chinanews.com/gn/2015/03-17/7136760.shtml']
    # start_urls=['http://news.tom.com/2015-03-17/OKV9/02844694.html']
    # start_urls=['http://www.afinance.cn/new/gncj/201503/829193.html']
    # start_urls=['http://news.southcn.com/community/content/2015-03/17/content_120232147.htm']
    # start_urls=['http://blog.ifeng.com/article/35148399.html?touping']
    # start_urls=['http://news.ifeng.com/a/20150316/43351164_0.shtml']





    root_class='40度'
    #一级分类下面的频道
    default_channel='最热门'
     #源网站的名称
    sourceSiteName={'focus':'谷歌焦点新闻','nondomestic':'谷歌国际/港台新闻','domestic':'谷歌内地新闻','finance':'谷歌财经新闻','entertainment':'谷歌娱乐新闻','tech':'谷歌科技新闻','sport':'谷歌体育新闻'}


    url_pattern=re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    page_url_pattern=re.compile(r'^http://world\.yam\.com/post\.php\?id=\d+?$')

    total_pages_pattern=re.compile(r'<span class="page-ch">.*?(\d+).*?</span>')
    page_lists_pat=re.compile(r'<a href="(.*?)" class="page-en">\d+</a>')


    title_pat=re.compile(ur'(.+?)[_-▏]')

    partial_title_pat=re.compile(r'<span class="titletext">(.*?)</span>')

    tag_pat=re.compile(r'<a target="_blank" href=".+?">(.+?)</a>')

    time_pat=re.compile(r'<span class="al-attribution-timestamp">(.*?)</span>')
    digital_pat=re.compile(r'\d+')

    content_pat=re.compile(r'<p>.*?</p>|<img.*?>',re.DOTALL)

    img_pat=re.compile(r'<img\s*?class=".*?"\s*?src="(.*?)"\s*?data-original=".*?"\s*?alt=".*?">')
    para_pat=re.compile(r'<p>(.*?)</p>',re.DOTALL)

    previous_page_pat=re.compile(r'<a href="(.*?)">»</a>')

    nonpage_url_pat=re.compile(r'<h2 class="esc-lead-article-title"><a.*?url="(.*?)"[^>]*?><span class="titletext">')
    # =re.compile(r'<h2 class="esc-lead-article-title"><a.*?url=".*?\.[s]?htm[l]?"[^>]*?><span class="titletext">|<span class="media-strip-item-state"><a.*?url=".*?\.[s]?htm[l]?"[^>]*?><div class="item-image-wrapper">')
    nonpage_url_pat_search=re.compile(r'<h2 class="esc-lead-article-title"><a.*?url="(.*?)"[^>]*?><span class="titletext">|<span class="media-strip-item-state"><a.*?url="(.*?\.[s]?htm[l]?)"[^>]*?><div class="item-image-wrapper">')
    # http://www.lensmagazine.com.cn/category/reporting/focus/page/4

    partial_description_pat=re.compile(r'<div class="esc-lead-snippet-wrapper">(.*?)</div>')


    bottom_page_pat=re.compile(r'<span class="media-strip-item-state"><a.*?url=".*?"[^<^>]*?><div class="item-image-wrapper">.*?</label>')
    bottom_page_url_pat=re.compile(r'<span class="media-strip-item-state"><a.*?url="(.*?)"[^<^>]*?><div class="item-image-wrapper">')
    # bottom_page_title_pat=re.compile(r'<label class="media-strip-item-label">(.*?)</label>')
    bottom_page_sourcesitename_pat=re.compile(r'<label class="media-strip-item-label">(.*?)</label>')


    middle_page_pat=re.compile(r'<div class="esc-secondary-article-title-wrapper"><a.*?url=".*?"[^<^>]*?><span.*?</label></div></div>')
    middle_page_url_pat=re.compile(r'<div class="esc-secondary-article-title-wrapper"><a.*?url="(.*?)"[^<^>]*?><span')

    middle_page_title_pat=re.compile(r'<span class="titletext">(.*?)</span>')

    middle_page_sourcesitename_pat=re.compile(ur'<label class=".*?">([^观点深入报道<>]*?)</label>')


    opinion_page_pat=re.compile(ur'<label class="esc-diversity-article-category">观点：</label><a.*?url=".*?"[^<^>]*?><span.*?</label>')
    opinion_page_url_pat=re.compile(ur'<label class="esc-diversity-article-category">观点：</label><a.*?url="(.*?)"[^<^>]*?><span')
    # opinion_page_title_pat=re.compile(r'<span class="titletext">(.*?)</span>')
    # opinion_page_sourcesitename_pat=re.compile(r'<label class=".*?">(.*?)</label>')

    deep_report_page_pat=re.compile(ur'<label class="esc-diversity-article-category">深入报道：</label><a.*?url=".*?"[^<^>]*?><span.*?</label>')
    deep_report_page_url_pat=re.compile(ur'<label class="esc-diversity-article-category">深入报道：</label><a.*?url="(.*?)"[^<^>]*?><span')
    # deep_report_page_title_pat=re.compile(r'<span class="titletext">(.*?)</span>')
    # deep_report_page_sourcesitename_pat=re.compile(r'<label class=".*?">(.*?)</label>')

    left_page_pat=re.compile(r'<div class="esc-thumbnail-wrapper"><div class="esc-thumbnail-state"><div class="esc-thumbnail".*?><a.*?url=".*?"[^<^>]*?><div.*?</label>')
    left_page_url_pat=re.compile(r'<div class="esc-thumbnail-wrapper"><div class="esc-thumbnail-state"><div class="esc-thumbnail".*?><a.*?url="(.*?)"[^<^>]*?><div')

    originsourceSiteName_pat=re.compile(r'<span class="al-attribution-source">(.*?)</span>')


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
        if  not  self.isPage(response,url):
            yield self.dealWithPage(response,url)
        else:
            results=self.dealWtihNonPage(response,url)

            for result in results:
                yield(result)


    def isPage(self,response,url):
        if None==url:
            return False
        if url.endswith(".html") or url.endswith(".shtml") or url.endswith(".htm") or url.endswith("html?touping"):
            return True
        return False



    def dealWithPage(self,response,url):
        # item 的唯一标识 用源网址
        item=NewsItem()
        item['root_class']=self.extractRootClass(response)
        # item['updateTime']=self.extractTime(response)
        item['title']=self.extractTitle(url)
        item['content']=self.extractContent(url)
        item['imgUrl']=self.extractImgUrl(url)
        item['sourceUrl']=url
        item['sourceSiteName']=self.extractSourceSiteName(response)
        item['tag']=self.extractTag(response)
        item['description']=self.extractDesc(response)
        item['channel']=self.extractChannel(response,item)
        item['_id']=self.generateItemId(item)

#        item.printSelf()
        return item


    def generateItemId(self,item):
        return item['sourceUrl']

    # def extractTitle(self,response):
    #
    #     raw_title_str=response.xpath('//article[@class="mainBox xxx"]/header').extract()[0]
    #     # raw_title_str=response.xpath('//div[@class="headerBar"]').extract()[0]
    #     searchResult1=re.search(self.title_pat1,raw_title_str)
    #
    #     if searchResult1:
    #         title=searchResult1.group(1)
    #         # title=searchResult1.group(1)
    #         return title
    #     return None


    def extractTitle(self,sourceUrl):
        if self.isFilterWebsite(sourceUrl):
            return None
        else:
            rawContent=self.getHtmlContentUnicode(sourceUrl)
        if rawContent==None:
            return None

        reader = StringReader(rawContent)
        source = BoilerpipeSAXInput(InputSource(reader)).getTextDocument()
        title=source.getTitle()

        # extractor = jpype.JClass("de.l3s.boilerpipe.sax.ImageExtractor").INSTANCE
        # images = extractor.process(source, rawContent)
        # jpype.java.util.Collections.sort(images)

        # extractor = Extractor(extractor='de.l3s.boilerpipe.sax.ImageExtractor', html=rawContent)
        # extractor_title=extractor.getImages()   #getTitle()
        # final ImageExtractor ie = ImageExtractor.INSTANCE;
        # images = ie.process(url,extractor);

        # extractor = Extractor(extractor='ArticleExtractor', html=rawContent)
        # extracted_title = extractor.getText()
        # extracted_text=self.removeUnWantedBeginnings(extracted_text)
        print "extracted_title1,%s"%title
        title=self.removeUnWantedTitle(title)
        # title=title.split('▏ ')[0]

        print "extracted_title2,%s"%title
        return title

    def removeUnWantedTitle(self,title_str):

        searchResult=re.search(self.title_pat,title_str)

        if searchResult:
            title=searchResult.group(1)
            return title
        return None




    def extractTime(self,response):

        # raw_time_str=response.xpath('//td[@class="al-attribution-cell timestamp-cell"]/span[@class="al-attribution-timestamp"]').extract()
        # print "raw,%s"%raw_time_str
        searchResult=re.search(self.time_pat,str(response))
        if searchResult:
            time=searchResult.group(1)
            # timestr=time.decode('unicode-escape')
            # timestr=timestr.encode('utf8')
            timestr=time
            digitals=re.findall(self.digital_pat,timestr)
            format='%Y-%m-%d %H:%M:%S'
            # timeDelta=datetime.timedelta(milliseconds=3600*1000)
            # defaultTime=(datetime.datetime.now()-timeDelta)
            # defaultTimeStr=defaultTime.strftime(format)
            # return defaultTimeStr

            if  timestr.endswith('分钟前‎'):
                timeDelta=datetime.timedelta(milliseconds=60*1000*int(digitals[0]))
                defaultTime=(datetime.datetime.now()-timeDelta)


            elif  timestr.endswith('小时前‎'):
                timeDelta=datetime.timedelta(milliseconds=3600*1000*int(digitals[0]))
                defaultTime=(datetime.datetime.now()-timeDelta)

            elif timestr.endswith('天前'):
                timeDelta=datetime.timedelta(milliseconds=24*3600*1000*int(digitals[0]))
                defaultTime=(datetime.datetime.now()-timeDelta)

            elif timestr.endswith('周前'):
                timeDelta=datetime.timedelta(milliseconds=7*24*3600*1000*int(digitals[0]))
                defaultTime=(datetime.datetime.now()-timeDelta)


            elif timestr.endswith('月前'):
                timeDelta=datetime.timedelta(milliseconds=4*7*24*3600*1000*int(digitals[0]))
                defaultTime=(datetime.datetime.now()-timeDelta)

            elif timestr.endswith('年前'):
                timeDelta=datetime.timedelta(milliseconds=12*4*7*24*3600*1000*int(digitals[0]))
                defaultTime=(datetime.datetime.now()-timeDelta)
            else:
                return CrawlerUtils.getDefaultTimeStr()
        else:
            return CrawlerUtils.getDefaultTimeStr()

        defaultTimeStr=defaultTime.strftime(format)
        return defaultTimeStr

    def extractcreateTime(self,response):
        return CrawlerUtils.getDefaultTimeStr()

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



    def isFilterWebsite(self,url):
        if None==url:
            return True
        for not_allowed_url in self.not_allowed_domains:
            if not_allowed_url in url:
                return True
        return False

    def getHtmlContentUnicode(self,url):
        # headers={'User-Agent': 'Mozilla/5.0'}
        try:
            request=urllib2.Request(url)
            connection=urllib2.urlopen(request,timeout=5)
            data=connection.read()
            encoding=connection.headers['content-type'].lower().split('charset=')[-1]
            if encoding.lower() == 'text/html':
                encoding = charade.detect(data)['encoding']
            # if encoding.lower()=='gb2312':
            #     encoding='gbk'
            if encoding:
                data = data.decode(encoding=encoding,errors='ignore')
            return data
        except Exception,e:
            print str(e)
            return None

    def removeUnWantedBeginnings(self,content):
        contentParas=content.split('\n')
        deleteMode=True
        resultArr=[]
        for para in contentParas:
            resultPara=None
            if not deleteMode:
                resultPara=self.formatSentence(para)
            else:
                checkState=self.isUnwantedBeginnings(para)
                if not checkState:
                    deleteMode=False
                    resultPara=self.formatSentence(para)
            if resultPara:
                resultArr.append(resultPara)

        return ''.join(resultArr)

    def formatSentence(self,para):
        if para==None:
            return None
        if CrawlerUtils.isAllSpaces(para):
            return None
        result=para

        result=result.replace('\t','')
        result=result.replace(u'\xa0', '')
        result=result.replace(CrawlerUtils.Q_space,'')
        result=result.strip()
        result=CrawlerUtils.Q_space+CrawlerUtils.Q_space+result+'\n\n'
        return result

    def isUnwantedBeginnings(self,para):
        fromSoureBeginPat=re.compile(r'^来源[：:]')
        unWantedBegining='分享到：'
        paraArr=re.split(re.compile(r'\s+'),para)
        for elem in paraArr:
            if re.match(fromSoureBeginPat,elem):
                return True
        if len(paraArr)>3:
            return True
        if para.startswith(unWantedBegining):
            return True
        return False

    def extractContent(self,sourceUrl):
        if self.isFilterWebsite(sourceUrl):
            return None
        else:
            rawContent=self.getHtmlContentUnicode(sourceUrl)
        if rawContent==None:
            return None
        extractor = Extractor(extractor='ArticleExtractor', html=rawContent)
        extracted_text = extractor.getText()
        extracted_text=self.removeUnWantedBeginnings(extracted_text)
        print "extracted_text,%s"%extracted_text
        return extracted_text



    def extractImgUrl(self,sourceUrl):
        if self.isFilterWebsite(sourceUrl):
            return None
        else:
            rawContent=self.getHtmlContentUnicode(sourceUrl)
        if rawContent==None:
            return None

        reader = StringReader(rawContent)
        source = BoilerpipeSAXInput(InputSource(reader)).getTextDocument()
        # title=source.getTitle()

        # extractor = jpype.JClass("de.l3s.boilerpipe.sax.ImageExtractor").INSTANCE
        # images = extractor.process(source, rawContent)
        # jpype.java.util.Collections.sort(images)

        extractor = Extractor(extractor='de.l3s.boilerpipe.sax.ImageExtractor', html=rawContent)
        extractor_title=extractor.getImages()   #getTitle()
        # final ImageExtractor ie = ImageExtractor.INSTANCE;
        # images = ie.process(url,extractor);

        # extractor = Extractor(extractor='ArticleExtractor', html=rawContent)
        # extracted_title = extractor.getText()
        # extracted_text=self.removeUnWantedBeginnings(extracted_text)
        print "extracted_title1,%s"%title
        title=self.removeUnWantedTitle(title)
        print "extracted_title2,%s"%title

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



    #处理不是页面的网址
    def dealWtihNonPage(self,response,url):
        pages_arr=response.xpath('//div[@id="body"]/div[@id="content"]/div/div[@class="column"]/div[@class="post"]/h2/a/@href').extract()
        focus_pages_arr=response.xpath('//div[@class="section top-stories-section"]/div[@class="section-content"]/div/div/div/div[@class="esc-body"]')  #/li[@class="box masonry-brick"


        request_items=[]
        for theme_page in focus_pages_arr:
            partial_item,url_list=self.generatePartialItem(theme_page)
            partial_item['sourceSiteName']=self.sourceSiteName['focus']
            if partial_item:
                request_items.append(partial_item)
            #     MongoUtils.saveGoogleItem(partial_item)
            # for url in url_list:
            #     print "Url is %s" %url
            #
                # request_items.append(scrapy.Request(url,callback=self.parse,dont_filter=False))

        nondomestic_pages_arr=response.xpath('//div[@class="section-list"]/div[@class="section-list-content"]/div[@class="section story-section section-zh-CN_cn-w"]/div/div/div/div[@class="esc-body"]')  #/li[@class="box masonry-brick"

        for theme_page in nondomestic_pages_arr:
            partial_item,url_list=self.generatePartialItem(theme_page)
            partial_item['sourceSiteName']=self.sourceSiteName['nondomestic']
            if partial_item:
                request_items.append(partial_item)
            #     MongoUtils.saveGoogleItem(partial_item)
            # for url in url_list:
            #     print "Url is %s" %url
                # request_items.append(scrapy.Request(url,callback=self.parse,dont_filter=False))


        domestic_pages_arr=response.xpath('//div[@class="section-list"]/div[@class="section-list-content"]/div[@class="section story-section section-zh-CN_cn-n"]/div/div/div/div[@class="esc-body"]')  #/li[@class="box masonry-brick"

        for theme_page in domestic_pages_arr:
            partial_item,url_list=self.generatePartialItem(theme_page)
            partial_item['sourceSiteName']=self.sourceSiteName['domestic']
            if partial_item:
                request_items.append(partial_item)
            #     MongoUtils.saveGoogleItem(partial_item)
            # for url in url_list:
            #     print "Url is %s" %url
            #     # request_items.append(scrapy.Request(url,callback=self.parse,dont_filter=False))


        finance_pages_arr=response.xpath('//div[@class="section-list"]/div[@class="section-list-content"]/div[@class="section story-section section-zh-CN_cn-b"]/div/div/div/div[@class="esc-body"]')  #/li[@class="box masonry-brick"

        for theme_page in finance_pages_arr:
            partial_item,url_list=self.generatePartialItem(theme_page)
            partial_item['sourceSiteName']=self.sourceSiteName['finance']
            if partial_item:
                request_items.append(partial_item)
            #     MongoUtils.saveGoogleItem(partial_item)
            # for url in url_list:
            #     print "Url is %s" %url
            #     # request_items.append(scrapy.Request(url,callback=self.parse,dont_filter=False))

        entertainment_pages_arr=response.xpath('//div[@class="section-list"]/div[@class="section-list-content"]/div[@class="section story-section section-zh-CN_cn-e"]/div/div/div/div[@class="esc-body"]')  #/li[@class="box masonry-brick"

        for theme_page in entertainment_pages_arr:
            partial_item,url_list=self.generatePartialItem(theme_page)
            partial_item['sourceSiteName']=self.sourceSiteName['entertainment']
            if partial_item:
                request_items.append(partial_item)
            #     MongoUtils.saveGoogleItem(partial_item)
            # for url in url_list:
            #     print "Url is %s" %url
            #     # request_items.append(scrapy.Request(url,callback=self.parse,dont_filter=False))


        tech_pages_arr=response.xpath('//div[@class="section-list"]/div[@class="section-list-content"]/div[@class="section story-section section-zh-CN_cn-t"]/div/div/div/div[@class="esc-body"]')  #/li[@class="box masonry-brick"

        for theme_page in tech_pages_arr:
            partial_item,url_list=self.generatePartialItem(theme_page)
            partial_item['sourceSiteName']=self.sourceSiteName['tech']
            if partial_item:
                request_items.append(partial_item)
            #     print "hello"
            #     MongoUtils.saveGoogleItem(partial_item)
            # for url in url_list:
            #     print "Url is %s" %url
            #     # request_items.append(scrapy.Request(url,callback=self.parse,dont_filter=False))


        sport_pages_arr=response.xpath('//div[@class="section-list"]/div[@class="section-list-content"]/div[@class="section story-section section-zh-CN_cn-s"]/div/div/div/div[@class="esc-body"]')  #/li[@class="box masonry-brick"

        for theme_page in sport_pages_arr:
            partial_item,url_list=self.generatePartialItem(theme_page)
            partial_item['sourceSiteName']=self.sourceSiteName['sport']

            if partial_item:
                request_items.append(partial_item)
                # MongoUtils.saveGoogleItem(partial_item)
            # for url in url_list:
            #     print "Url is %s" %url
            #     request_items.append(scrapy.Request(url,callback=self.parse,dont_filter=False))


        return request_items


    def generatePartialItem(self,theme_page):

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
            partial_item['description']=description[0]
            print "description,%s"%partial_item['description']

            originsourceSiteName=re.findall(self.originsourceSiteName_pat,theme_page)
            partial_item['originsourceSiteName']=originsourceSiteName[0]
            print "originsourceSiteName,%s"%partial_item['originsourceSiteName']
            # partial_item['updateTime']=CrawlerUtils.getDefaultTimeStr()
            partial_item['updateTime']=self.extractTime(theme_page)

            partial_item['createTime']=self.extractcreateTime(theme_page)


            url_list=[]
            url_list.append(partial_item['sourceUrl'])

            relate={}


            bottom=[]
            middle=[]
            opinion=[]
            deep_report=[]
            left=[]

            # bottom_page=re.findall(self.bottom_page_pat,theme_page)
            # for new_page in bottom_page:
            #     bottomItem={}
            #     new_page_url=re.search(self.bottom_page_url_pat,new_page)
            #     if new_page_url:
            #         new_page_url=new_page_url.group(1)
            #         print "bottom_new_page_url,%s"%new_page_url
            #
            #     new_page_sourcesitename=re.search(self.bottom_page_sourcesitename_pat,new_page)
            #     if new_page_sourcesitename:
            #         new_page_sourcesitename=new_page_sourcesitename.group(1)
            #         print "bottom_new_page_sourcesitename,%s"%new_page_sourcesitename
            #     bottomItem['url']=new_page_url
            #     bottomItem['sourceSitename']=new_page_sourcesitename
            #     bottomItem['title']=None
            #     bottom.append(bottomItem)
            #     # bottom.append()
            #     # related.append(({'bottom':new_page_url}))
            #     url_list.append(new_page_url)


            middle_page=re.findall(self.middle_page_pat,theme_page)
            for new_page in middle_page:
                middleItem={}
                new_page_url=re.search(self.middle_page_url_pat,new_page)
                if new_page_url:
                    new_page_url=new_page_url.group(1)
                    print "middle_new_page_url,%s"%new_page_url

                new_page_title=re.search(self.middle_page_title_pat,new_page)
                if new_page_title:
                    new_page_title=new_page_title.group(1)
                    print "middle_new_page_title,%s"%new_page_title
                new_page_sourcesitename=re.search(self.middle_page_sourcesitename_pat,new_page)
                if new_page_sourcesitename:
                    new_page_sourcesitename=new_page_sourcesitename.group(1)
                    print "middle_new_page_sourcesitename,%s"%new_page_sourcesitename


                middleItem['url']=new_page_url
                middleItem['sourceSitename']=new_page_sourcesitename
                middleItem['title']=new_page_title
                # related_url.append(({'middle':new_page_url}))
                middle.append(middleItem)
                url_list.append(new_page_url)

            opinion_page=re.findall(self.opinion_page_pat,theme_page)

            if opinion_page:

                opinionItem={}
                for new_page in opinion_page:
                    new_page_url=re.search(self.opinion_page_url_pat,new_page)
                    if new_page_url:
                        new_page_url=new_page_url.group(1)
                        print "opinion_new_page_url,%s"%new_page_url

                    new_page_title=re.search(self.middle_page_title_pat,new_page)
                    if new_page_title:
                        new_page_title=new_page_title.group(1)
                        print "opinion_new_page_title,%s"%new_page_title
                    new_page_sourcesitename=re.search(self.middle_page_sourcesitename_pat,new_page)
                    if new_page_sourcesitename:
                        new_page_sourcesitename=new_page_sourcesitename.group(1)
                        print "opinion_new_page_sourcesitename,%s"%new_page_sourcesitename

                    opinionItem['url']=new_page_url
                    opinionItem['sourceSitename']=new_page_sourcesitename
                    opinionItem['title']=new_page_title
                     # related_url.append(({'middle':new_page_url}))
                    opinion.append(opinionItem)
                    url_list.append(new_page_url)

                    print "opinion_new_page_url,%s"%new_page_url

                    # related_url.append(({'opinion':new_page_url}))
                    url_list.append(new_page_url)


            deep_report_page=re.findall(self.deep_report_page_pat,theme_page)
            if deep_report_page:
                deep_reportItem={}
                for new_page in deep_report_page:
                    new_page_url=re.search(self.deep_report_page_url_pat,new_page)
                    if new_page_url:
                        new_page_url=new_page_url.group(1)
                        print "deep_report_new_page_url,%s"%new_page_url

                    new_page_title=re.search(self.middle_page_title_pat,new_page)
                    if new_page_title:
                        new_page_title=new_page_title.group(1)
                        print "deep_report_new_page_title,%s"%new_page_title

                    new_page_sourcesitename=re.search(self.middle_page_sourcesitename_pat,new_page)
                    if new_page_sourcesitename:
                        new_page_sourcesitename=new_page_sourcesitename.group(1)
                        print "deep_report_new_page_sourcesitename,%s"%new_page_sourcesitename

                    deep_reportItem['url']=new_page_url
                    deep_reportItem['sourceSitename']=new_page_sourcesitename
                    deep_reportItem['title']=new_page_title
                     # related_url.append(({'middle':new_page_url}))
                    deep_report.append(deep_reportItem)
                    url_list.append(new_page_url)
                    print "deep_report_new_page_url,%s"%new_page_url
                    # related_url.append(({'deep_report':new_page_url}))
                    url_list.append(new_page_url)

            left_page=re.findall(self.left_page_pat,theme_page)
            if left_page:
                leftItem={}
                for new_page in left_page:
                    new_page_url=re.search(self.left_page_url_pat,new_page)
                    if new_page_url:
                        new_page_url=new_page_url.group(1)
                        print "left_new_page_url,%s"%new_page_url

                    new_page_sourcesitename=re.search(self.middle_page_sourcesitename_pat,new_page)
                    if new_page_sourcesitename:
                        new_page_sourcesitename=new_page_sourcesitename.group(1)
                        print "left_new_page_sourcesitename,%s"%new_page_sourcesitename

                    leftItem['url']=new_page_url
                    leftItem['sourceSitename']=new_page_sourcesitename
                    leftItem['title']=None
                    left.append(leftItem)

                    # related_url.append(({'left':new_page_url}))
                    url_list.append(new_page_url)
            relate['bottom']=bottom
            relate['middle']=middle
            relate['opinion']=opinion
            relate['deep_report']=deep_report
            relate['left']=left

            partial_item['relate']=relate
            partial_item['root_class']=self.root_class
            partial_item['channel']=self.default_channel
            # partial_item['sourceSiteName']=self.sourceSiteName
            # partial_item['imgUrls']=None

            return partial_item,url_list



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

    # def generatePartialItem(self,dom_elem,tag,city,parentUrl):
    #     partial_item=PartialNewsItem()
    #     partial_item['tag']=tag
    #     partial_item['city']=city
    #     print "city is %s" %city
    #
    #
    #     source_url_arr=dom_elem.xpath('./a/@href').extract()
    #     if not len(source_url_arr):
    #         return None
    #     source_url=source_url_arr[0]
    #     if  not source_url.startswith('http'):
    #         baseUrl=self.extractBaseUrl(parentUrl)
    #         if baseUrl:
    #             source_url=baseUrl+source_url
    #     partial_item['sourceUrl']=source_url
    #     partial_item['_id']=source_url
    #     partial_item['imgUrl']=dom_elem.xpath('./a/img/@src').extract()[0]
    #     partial_item['title']=dom_elem.xpath('./div[@class="info"]/h2/a/text()').extract()[0]
    #     partial_item['description']=dom_elem.xpath('./div[@class="info"]/p/text()').extract()[0]
    #     return partial_item




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

    timestr='‎7小时前‎'
    # timestr='7小时前'
    print timestr.endswith('小时前‎')


    print timestr.endswith(u'小时前')
    # url = "http://www.l3s.de/web/page11g.do?sp=page11g&link=ln104g&stu1g.LanguageISOCtxParam=en";

     # This can also be done in one line:
    # txt=DefaultExtractor.INSTANCE.getText(url));
