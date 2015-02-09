# #coding=utf-8
# from news_spider_version2.items import NewsItem, PartialNewsItem
# from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils
# from news_spider_version2.spiders.utils.MongoUtils import MongoUtils
#
#
# __author__ = 'galois'
#
# import scrapy
# import re
#
# import HTMLParser
#
#
# class TtpetSpider(scrapy.Spider):
#     name='ttpetSpider'
#     allowed_domains=['www.ttpet.com']
#
#     start_urls=['http://www.ttpet.com/zixun/39/category-catid-39.html']
#     # start_urls=['http://www.douban.com/note/427790805']
#
#     root_class='36度'
#     #一级分类下面的频道
#     default_channel='暖心'
#      #源网站的名称
#     sourceSiteName='天天宠物网'
#
#
#     page_url_pattern=re.compile(r'^http://www\.ttpet\.com/zixun/\d+/n-\d+\.html$')
#     non_page_url_pattern=re.compile(r'^http://www\.ttpet\.com/zixun/\d+/category-catid-\d+\.html$')
#
#     time_pat=re.compile(r'</a>\s*?@\s*([\d\. ,:]+\w+)\s*?</div>')
#
#     content_pat=re.compile(r'\s*[^>]*?\s*<br>|<img(?: .*?)? src=".*?"(?: .*?)?>')
#     img_pat=re.compile(r'<img(?: .*?)? src="(.*?)"(?: .*?)?>')
#     para_pat=re.compile(r'\s*([^>]*?)\s*<br>')
#
#     previous_page_pat=re.compile(ur'<a href="([\w:/\d\.]+)"(?: [^<>]+?)?>></a>')
#
#     html_parser = HTMLParser.HTMLParser()
#
#     def parse(self,response):
#         url=response._get_url()
#         page_test=self.isPage(response,url)
#         #不是要爬取的页面
#         if page_test==None:
#             return
#         if page_test:
#             yield self.dealWithPage(response,url)
#         else:
#             non_page_results,results=self.dealWithNonPage(response,url)
#             for non_page_result in non_page_results:
#                 yield(non_page_result)
#             for result in results:
#                 yield(result)
#
#     def isPage(self,response,url):
#         if None==url:
#             return None
#         if re.match(self.page_url_pattern,url):
#             return True
#         elif re.match(self.non_page_url_pattern,url):
#             return False
#         return None
#
#
#     def dealWithPage(self,response,url):
#         # item 的唯一标识 用源网址
#         item=NewsItem()
#
#         item['root_class']=self.extractRootClass(response)
#
#         item['updateTime']=self.extractTime(response)
#         item['title']=self.extractTitle(response)
#         item['content']=self.extractContent(response)
#         item['imgUrl']=self.extractImgUrl(response)
#         item['sourceUrl']=url
#         item['sourceSiteName']=self.extractSourceSiteName(response)
#         item['tag']=self.extractTag(response)
#         # item['edit_tag']=self.extractEditTag(response)
#         item['channel']=self.extractChannel(response,item)
#         item['_id']=self.generateItemId(item)
#         item['description']=self.extractDesc(response)
#         item.printSelf()
#         return item
#
#
#     def generateItemId(self,item):
#         return item['sourceUrl']
#
#     def extractTitle(self,response):
#         title=response.xpath('//div[@class="note-header note-header-container"]/h1/text()').extract()[0]
#         return title
#
#     def extractTime(self,response):
#         raw_time_str=response.xpath('//div[@class="note-header note-header-container"]/div/span/text()').extract()[0]
#         time=raw_time_str
#         return time
#
#     def extractRootClass(self,response):
#         return self.root_class
#
#     def extractChannel(self,response,item):
#         return self.default_channel
#
#     def extractContent(self,response):
#         rawContent=response.xpath('//div[@id="link-report"]').extract()[0]
#         return CrawlerUtils.extractContent(rawContent,self.content_pat,self.img_pat,self.para_pat)
#
#
#     def extractImgUrl(self,response):
#         rawContent=response.xpath('//div[@id="link-report"]').extract()
#         if not len(rawContent):
#             return None
#         for line in re.findall(self.content_pat,rawContent[0]):
#             imgSearch=re.search(self.img_pat,line)
#             if imgSearch:
#                 return imgSearch.group(1)
#         return None
#
#     def extractDesc(self,response):
#         return None
#
#     def extractSourceSiteName(self,response):
#         return self.sourceSiteName
#
#     #获取文章的tag信息
#     def extractTag(self,response):
#         # xpath_str='//div[@class="note_upper_footer"]/div[@class="footer-tags"]/a/text()'
#         # tag=response.xpath(xpath_str).extract()
#         # return tag
#         tag=[]
#         tag.append(self.default_tag)
#         return tag
#
#     #获取文章的tag信息
#     def extractEditTag(self,response):
#         # xpath_str='//div[@class="note_upper_footer"]/div[@class="footer-tags"]/a/text()'
#         # tag=response.xpath(xpath_str).extract()
#         # return tag
#        return self.default_tag;
#
#     #处理不是页面的网址
#     def dealWithNonPage(self,response,url):
#         xpath_str='//div[@class="article"]/div[@class="status-item"]/div[@class="mod"]/' \
#                   'div/div[@class="content"]/div[@class="title"]/a/@href'
#         pages_arr=response.xpath(xpath_str).extract()
#         request_items=[]
#         for elem in pages_arr:
#             request_items.append(scrapy.Request(elem,callback=self.parse,dont_filter=False))
#
#         non_page_results=[]
#         non_page_url=self.getPrevoiuPageUrl(response)
#         non_page_results.append(scrapy.Request(non_page_url,callback=self.parse,dont_filter=False))
#         return non_page_results,request_items
#
#
#      #获取前面一页的url
#     def getPrevoiuPageUrl(self,response):
#         xpath_str='//div[@class="paginator"]/span[@class="next"]/link/@href'
#         previousUrlsPath=response.xpath(xpath_str).extract()
#         if len(previousUrlsPath):
#             html_parser=HTMLParser.HTMLParser()
#             page_url_str=html_parser.unescape(previousUrlsPath[0])
#             return page_url_str
#         return None
#
#
#
# if __name__=='__main__':
#     # some_interface='http://jandan.duoshuo.com/api/threads/listPosts.json?thread_key=comment-2650694&url=http%3A%2F%2Fjandan.net%2Fooxx%2Fpage-1301%26yid%3Dcomment-2650694&image=http%3A%2F%2Fww1.sinaimg.cn%2Fmw600%2Fa00dfa2agw1enxg54qbbfj20n40x6755.jpg&require=site%2Cvisitor%2Cnonce%2CserverTime%2Clang&site_ims=1420356603&lang_ims=1420356603&v=140327'
#     # print "the interface is %s"%some_interface
#     # html_parser=HTMLParser.HTMLParser()
#     # print "the unscaped is %s " %html_parser.unescape(some_interface)
#     print "Hello world"
