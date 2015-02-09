#coding=utf-8
from scrapy.conf import settings
from selenium import webdriver
from news_spider_version2.items import NewsItem, PartialNewsItem
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils

import scrapy
import re
import HTMLParser


class WeixinSougouSpider(scrapy.Spider):
    name='WeixinSougou'
    allowed_domains=['weixin.sogou.com','mp.weixin.qq.com']

    start_urls=['http://weixin.sogou.com/gzh?openid=oIWsFt5HJEgGlbxXAB2hBcmwjQho',
                'http://weixin.sogou.com/gzh?openid=oIWsFt27e2suwc9YvYZIO4bLz7E0',
                'http://weixin.sogou.com/gzh?openid=oIWsFt-W8WxV7WDe0nnGz1SlLzwE&sourceid=weixinv',
                ]

    # start_urls=['http://weixin.sogou.com/gzh?openid=oIWsFt-W8WxV7WDe0nnGz1SlLzwE&sourceid=weixinv']
    # start_urls=['http://mp.weixin.qq.com/s?__biz=MjM5MDM4MDExNQ==&mid=209232805&idx=1&sn=51d3c72d49f13e1552d743a0ef07a7d1&3rd=MzA3MDU4NTYzMw==&scene=6#rd']

    root_class='36度'
    #一级分类下面的频道
    default_channel='同步喜好'
     #源网站的名称
    sourceSiteName='知乎日报'

    default_tag='涨姿势'

    root_class_map={'知乎日报':'36度','掌上北京':'36度','单读':'36度'}
    channel_map={'知乎日报':'同步喜好','单读':'同步喜好','掌上北京':'城市'}

    tag_map={'知乎日报':'涨姿势','单读':'有腔调'}

    page_url_pattern=re.compile(r'^http://mp.weixin.qq.com/s?__biz=.*')

    time_pat=re.compile(r'</a>\s*?@\s*([\d\. ,:]+\w+)\s*?</div>')
    digital_pat=re.compile(r'\d+')

    img_pat=re.compile(r'<img(?: .*?)? (?:data-)?src="(.*?)"(?: .*?)?>',re.DOTALL)
    content_pat=re.compile(r'<p(?: .*?)?>.*?</p>|<section(?: .*?)? class="tn-Powered-by-XIUMI"(?: .*?)?>.*?</section>|<img(?: .*?)? (?:data-)?src=".*?"(?: .*?)?>',re.DOTALL)
    para_pat=re.compile(r'<p(?: .*?)?>(.*?)</p>|<section(?: .*?)? class="tn-Powered-by-XIUMI"(?: .*?)?>(.*?)</section>')

    thumbnail_view_img=re.compile(r'var\s+cover\s*?=\s*?"(.*?)"')

    previous_page_pat=re.compile(ur'<a href="([\w:/\d\.]+)"(?: [^<>]+?)?>></a>')

    html_parser = HTMLParser.HTMLParser()

    def start_requests(self):
        urls=set([])
        for start_url in self.start_urls:
            page_urls=self.getPageUrlsFromSelenium(start_url)
            if page_urls:
                for page_url in page_urls:
                    urls.add(page_url)
        for url in urls:
            yield scrapy.Request(url,callback=self.parse,dont_filter=True)


    def getPageUrlsFromSelenium(self,url):
        caps={
        'takeScreenshot':False,
        'javascriptEnabled':True,
    }

        phantom_link=settings['PHANTOM_LINK']

        driver=webdriver.Remote(
            command_executor=phantom_link,
            desired_capabilities=caps
        )

        driver.get(url)
        # print driver.title
        results=[]
        elems=driver.find_elements_by_xpath('//*[@id="sogou_vr_11002601_box_0"]/div[@class="img_box2"]/a')
        for elem in elems:
            results.append(elem.get_attribute('href'))
        return results


    def parse(self,response):
        url=response._get_url()
        if self.isPage(response,url):
            yield self.dealWithPage(response,url)
        # else:
        #     results=self.dealWithNonPage(response,url)
        #     # for result in results:
        #     #     yield(result)

    def isPage(self,response,url):
        return True


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
        item['root_class']=self.extractRootClass(response)
        item['channel']=self.extractChannel(response,item)
        item['_id']=self.generateItemId(item)
        item.printSelf()
        return item


    def generateItemId(self,item):
        return item['sourceUrl']

    def extractTitle(self,response):
        xpath_str='//h2[@id="activity-name"]/text()'
        title=response.xpath(xpath_str).extract()[0]
        return title

    def extractTime(self,response):
        xpath_str='//div[@class="rich_media_meta_list"]/em[@id="post-date"]/text()'
        raw_time_str=response.xpath(xpath_str).extract()[0]
        time=raw_time_str
        return self.formatTime(time)

    def formatTime(self,timeStr):
        hour_to_second=CrawlerUtils.getDefaultTimeStr().split(' ')[-1];
        print "the hour_to_second is %s"%hour_to_second
        time=timeStr+' '+hour_to_second
        return time

    def extractRootClass(self,response):
        source_str=self.extractSourceSiteName(response)
        if source_str in self.root_class_map:
            return self.root_class_map[source_str]
        return self.root_class

    def extractChannel(self,response,item):
        source_str=self.extractSourceSiteName(response)
        if source_str in self.channel_map:
            return self.channel_map[source_str]
        return self.default_channel

    def extractContent(self,response):
        xpath_str='//div[@id="js_content"]'
        rawContent=response.xpath(xpath_str).extract()[0]
        # rawContent='<fieldset style="border: 0px; box-sizing: border-box; width: 100%; margin: 0.8em 0px 0.2em; clear: both; padding: 0px;" class="tn-Powered-by-XIUMI"><img style="box-sizing: border-box; width: 100% !important; visibility: visible !important; height: auto !important;" data-src="http://mmbiz.qpic.cn/mmbiz/hFB4FUPIIlKAyfaFgyBVvLrNDaAic0UCW7f93yg9jV8bHWQvHlCibtWAiaDvdwSE1Ya0CmQKFXkJwOblWEsvSl4YA/0" class="tn-Powered-by-XIUMI" id="c1423040231618" data-type="png" data-ratio="0.6732283464566929" data-w="508" _width="100%" src="http://mmbiz.qpic.cn/mmbiz/hFB4FUPIIlKAyfaFgyBVvLrNDaAic0UCW7f93yg9jV8bHWQvHlCibtWAiaDvdwSE1Ya0CmQKFXkJwOblWEsvSl4YA/0?tp=webp&amp;wxfrom=5"></fieldset>'
        return CrawlerUtils.extractContent(rawContent,self.content_pat,self.img_pat,self.para_pat)


    def extractImgUrl(self,response):
        xpath_str='//div[@id="media"]'
        rawContent=response.xpath(xpath_str).extract()
        if not len(rawContent):
            return None
        searchResult=re.search(self.thumbnail_view_img,rawContent[0])
        if searchResult:
            return searchResult.group(1)
        return None

    def extractDesc(self,response):
        return None

    def extractSourceSiteName(self,response):
        xpath_str='//div[@class="rich_media_meta_list"]/a/text()'
        source_str=response.xpath(xpath_str).extract()[0].encode('utf-8')
        return source_str

    #获取文章的tag信息
    def extractTag(self,response):
        tag=response.xpath('//ul[@class="post-tags"]/li/a[@rel="tag"]/text()').extract()
        return tag

    def extractEditTag(self,response):
        source_str=self.extractSourceSiteName(response)
        if source_str in self.tag_map:
            return self.tag_map[source_str]
        return None

    #处理不是页面的网址
    def dealWithNonPage(self,response,url):
        pages_arr=response.xpath('//div[@class="result"]').extract()
        request_items=[]
        for elem in pages_arr:
            request_items.append(scrapy.Request(elem,callback=self.parse,dont_filter=False))
            print "the child url is %s"%elem

        return request_items

    def generatePartialItem(self,dom_elem):
        partial_item=PartialNewsItem()

        source_url_arr=dom_elem.xpath('./div[@class="image"]/a/@href').extract()
        if not len(source_url_arr):
            return None
        source_url=source_url_arr[0]
        partial_item['sourceUrl']=source_url
        partial_item['_id']=source_url
        partial_item['imgUrl']=dom_elem.xpath('./div[@class="image"]/a/img/@src').extract()[0]
        partial_item['title']=dom_elem.xpath('./div[@class="image"]/a/@title').extract()[0]
        partial_item['description']=dom_elem.xpath('./div[@class="information"]/p/text()').extract()[0]
        return partial_item

     #获取前面一页的url
    def getPrevoiuPageUrl(self,response):
        previousUrlsPath=response.xpath('//div[@class="pagging"]/div[@class="pagging_inside"]').extract()
        if len(previousUrlsPath):
            html_parser=HTMLParser.HTMLParser()
            page_url_str=html_parser.unescape(previousUrlsPath[0])

            search_result=re.search(self.previous_page_pat,page_url_str)
            if search_result:
                return search_result.group(1)
        return None



    def main(self,url):
       urlStr=self.getHtmlContentUnicode(url)
       print urlStr

if __name__=='__main__':


    rawContent='<fieldset style="border: 0px; box-sizing: border-box; width: 100%; margin: 0.8em 0px 0.2em; clear: both; padding: 0px;" class="tn-Powered-by-XIUMI"><img style="box-sizing: border-box; width: 100% !important; visibility: visible !important; height: auto !important;" data-src="http://mmbiz.qpic.cn/mmbiz/hFB4FUPIIlKAyfaFgyBVvLrNDaAic0UCW7f93yg9jV8bHWQvHlCibtWAiaDvdwSE1Ya0CmQKFXkJwOblWEsvSl4YA/0" class="tn-Powered-by-XIUMI" id="c1423040231618" data-type="png" data-ratio="0.6732283464566929" data-w="508" _width="100%" src="http://mmbiz.qpic.cn/mmbiz/hFB4FUPIIlKAyfaFgyBVvLrNDaAic0UCW7f93yg9jV8bHWQvHlCibtWAiaDvdwSE1Ya0CmQKFXkJwOblWEsvSl4YA/0?tp=webp&amp;wxfrom=5"></fieldset>'
    spider=WeixinSougouSpider()
    for line in re.findall(spider.content_pat,rawContent):
        print "line is %s" %line
    search_result=re.search(spider.img_pat,rawContent)
    if search_result:
        print "the img url is %s" %search_result.group(1)
