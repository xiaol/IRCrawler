#coding=utf-8
import re
import scrapy
from news_spider_version2.spiders.SportsBaseSpider import SportsBaseSpider
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils

class SinaSportsSpider(SportsBaseSpider):
    name='SportsSinaSpider'
    allowed_domains=['sports.sina.com.cn']
    # start_urls=['http://sports.sina.com.cn/']
    start_urls=['http://sports.sina.com.cn/g/laliga/2014-12-q/10217456696.shtml']

    source_site='新浪体育'

    disallowed_domains=['sina.com.cn/l/','sina.aicai.com/','game.sports.sina.com.cn/',
                        'sports.sina.com.cn/games/','forum.sports.sina.com.cn/',
                        'sports.sina.com.cn/bbs/','blog.sina.com.cn/',
                        'match.sports.sina.com.cn/','video.sina.com.cn/',
                        'slide.sports.sina.com.cn/','guess.sports.sina.com.cn',
                        'odds.sports.sina.com.cn','sports.sina.com.cn/star/']

    category_pattern=re.compile(r'<a href=.*?>(.*?)</a>')
    digit_pattern=re.compile(r'\d+')
    img_pattern=re.compile(r'<div (?:.* )?class="img_wrapper"(?: .*?)?>\s*?<img(?: .*?)? src="(.*?)"',re.DOTALL)
    paragraph_Pat=re.compile(r'(?:(?:<p>)|(?:<p .*?>))(.*?)</p>',re.DOTALL)
    tagPatDel=re.compile(r'<.*?>',re.DOTALL)

    def isPage(self,response,url):
        '''
        判断是否是网页
        :param response:
        :param url:
        :return:
        '''
        rawContent=response.xpath('//div[@id="artibody"]').extract()
        if len(rawContent):
            return True
        return False

    #提取title
    def extractTitle(self,response):
        titleArr=response.xpath('//h1[@id="artibodyTitle"]/text()').extract()
        if not len(titleArr):
            titleArr=response.xpath('//h1[@id="artibodyTitle"]/font/text()').extract()
        title=titleArr[0].encode("utf-8")
        return title

    #提取description
    def extractDesc(self,response):
        return None


    #提取imgurl
    def extractImgUrl(self,response):
        rawContent=response.xpath('//div[@id="artibody"]').extract()
        lineArr=rawContent[0].split('\n')
        for line in lineArr:
            imgSearch=re.search(self.img_pattern,line)
            if imgSearch:
                return imgSearch.group(1)
        return None

    #提取正文
    def extractMainText(self,response):
        rawContent=response.xpath('//div[@id="artibody"]').extract()
        lineArr=rawContent[0].split('\n')
        img_text_infos=[]
        listInfos=[]
        for line in lineArr:
            imgSearch=re.search(self.img_pattern,line)
            if imgSearch:
                listInfos.append({'img':imgSearch.group(1)})
            else:
                txtSearch=re.search(self.paragraph_Pat,line)
                if txtSearch:
                    result=txtSearch.group(1)
                    result=CrawlerUtils.removeParasedCode(result)
                    result=CrawlerUtils.removeScript(result)
                    result=re.sub(self.tagPatDel,'',result)
                    if (not CrawlerUtils.isAllSpaces(result)) & (not CrawlerUtils.isPagesInfo(result)):
                        result=CrawlerUtils.Q_space+CrawlerUtils.Q_space+result+'\n\n'
                        listInfos.append({'txt':result})
                        print "txt : %s" %result
        return CrawlerUtils.make_img_text_pair(listInfos)

    #提取时间
    def extractTime(self,response):
        rawTimeContentArr=response.xpath('//div[@class="page-info"]/span[@class="time-source"]').extract()
        if len(rawTimeContentArr):
            return self.formatTime(rawTimeContentArr[0])
        rawTimeContentArr=response.xpath('//span[@id="pub_date"]/text()').extract()
        return self.formatTime(rawTimeContentArr[0])
        return self.formatTime(None)


    #format time
    def formatTime(self,timeStr):
        if timeStr==None:
            return CrawlerUtils.getDefaultTimeStr()
        s=re.findall(self.digit_pattern,timeStr)
        timeArr=[]
        if s:
            i=0
            for elem in s:
                if len(elem)<2:
                    timeArr.append('0')
                timeArr.append(elem)
                if i<2:
                    timeArr.append('-')
                elif i==2:
                    timeArr.append(' ')
                elif i<5:
                    timeArr.append(':')
                i=i+1

            if len(s)==5:
                timeArr.append(CrawlerUtils.getDefaultTimeStr().split(':')[-1])
        return ''.join(timeArr)

    #提取分类
    def extractCategory(self,response):
        rawCategoryArr=response.xpath('//div[@class="blkBreadcrumbLink"]').extract()
        category=None
        if len(rawCategoryArr):
            rawCategory=rawCategoryArr[0]
            search=re.search(self.category_pattern,rawCategory)
            category=search.group(1)
        else:
            rawCategoryArr=response.xpath('//div[@class="bread"]/a/text()').extract()
            if len(rawCategoryArr):
                category=rawCategoryArr[0]
        if category:
            category=category.encode('utf-8')
            category=CrawlerUtils.map_to_Category(category)
        return category

    def extractSubcategory(self,response):
        return None


    #提取标签tdr
    def extractTags(self,response):
        tagLists=[]
        rawCategoryArr=response.xpath('//div[@class="blkBreadcrumbLink"]').extract()
        if len(rawCategoryArr):
            rawCategory=rawCategoryArr[0].encode('utf-8')
            searchs=re.findall(self.category_pattern,rawCategory)
            if searchs:
                i=0
                for search in searchs:
                    if i>0:
                        tagLists.append(search)
                    i=i+1
        rawCategoryArr=response.xpath('//p[@class="art_keywords"]/a/text()').extract()
        if len(rawCategoryArr):
            for tag in rawCategoryArr:
                tagLists.append(tag)
        return tagLists

    def dealWtihNonPage(self,url,response):
        if url:
            if CrawlerUtils.isUrl(url):
                if not (url.endswith(".html") | url.endswith(".shtml")):
                    results=[]
                    for child_url in response.xpath('//a/@href').extract():
                        if CrawlerUtils.isUrl(child_url)&(child_url not in self.start_urls ):
                            if ('.html'in child_url) | ('.shtml' in child_url):
                                dontFilt=False
                            else:
                                dontFilt=True
                            if not self.isFilteredPage(child_url):
                                print "the appending url is %s" %child_url
                                results.append(scrapy.Request(child_url,callback=self.parse,dont_filter=dontFilt,priority=self.INITIAL_PRIORITY))
                    return results
        return None