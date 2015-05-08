#coding=utf-8
import urllib2

# import charade

# from myproject.spiders.utils import AreaReader, CrawlerUtils
import requests
import lxml.etree as etree

__author__ = 'galois'

import scrapy
import re
from news_spider_version2.items import CommentItem
# from boilerpipe.extract import Extractor
import urlparse
# from utils.AreaReader import AreaReader
# from utils.CrawlerUtils import CrawlerUtils
import urllib, cStringIO
# from PIL import Image
import json
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils

# 'scrapy crawl news.baidu.com -a url=' + url_here + ' -a topic=\"'+ topic + '\"'

class GoogleSearchSpider(scrapy.Spider):
    name='google.com.hk'
    allowed_domains=['google.com.hk']
    # keywords=AreaReader.readArea('/Users/galois/exercise/scrapy/myproject/AreaFile.txt')
    # https://www.google.com.hk/?gws_rd=ssl#safe=strict&q=site:163.com++%E7%BD%91%E6%9B%9D%E5%9B%9B%E5%B7%9D%E6%83%85%E4%BE%A3
    # file:///Users/yangjiwen/Documents/xiongjun/GoogleNewsHtml/https-::www.google.com.hk:%3Fgws_rd=ssl%23safe=strict&q=site-163.com++%25E7%25BD%2591%25E6%259B%259D%25E5%259B%259B%25E5%25B7%259D%25E6%2583%2585%25E4%25BE%25A3.html
    source_site="网易新闻"

    def __init__(self, url=None, topic=None, *args, **kwargs):

        super(GoogleSearchSpider, self).__init__(*args, **kwargs)
        # keywords = []
        self.start_urls=[]
        topic = topic.split('s')
        self.keyword = "%20".join(topic)
        self.relate_url = url
        print self.keyword, self.relate_url
        # for keyword in keywords:
        self.start_urls.append('https://www.google.com.hk/?gws_rd=ssl#safe=strict&q=site:163.com++%s'%self.keyword)
        # self.start_urls.append('file:///Users/yangjiwen/Documents/xiongjun/GoogleNewsHtml/com++%s.html'%self.keyword)
        for e in self.start_urls:
            print ">>>>>>", e

        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F\][0-9a-fA-F]))+')
        self.time_pattern = re.compile(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}|\d+小时前|\d{4}年\d{2}月\d{2}日 \d{2}:\d{2}')
        self.keyword_pattern = re.compile(r'http://news.baidu.com/ns\?word=(.*?)&.*?')
        self.comment_pattern = re.compile(r'boardId = "(.*?)"')
        self.infoStr_pattern = re.compile(r'replyData=({.*?});', re.DOTALL)



    def extractcomment(self,sourceUrl):

        r = requests.get(sourceUrl)
        dom = etree.HTML(r.text)
        print "r.txt,%s"%r.text

        # print "dom,%s"%dom.xpath('//div[@class="actions cf"][1]/a/text()')
        if len(dom.xpath('//div[@class="actions cf"]/a/@href')):
            commentUrl=dom.xpath('//div[@class="actions cf"][1]/a[2]/@href')[0]
            commentUrl="http://comment.news.163.com/data/"+commentUrl.split("/")[-2]+"/df/"+commentUrl.split("/")[-1]
            print commentUrl
            return commentUrl
        else:
            comment_result=re.search(self.comment_pattern, r.text)
            if comment_result:
                comment_result=comment_result.group(1)
                commentUrl="http://comment.news.163.com/data/"+comment_result+"/df/"+sourceUrl.split("/")[-1]
            # commentUrl=dom.xpath('//div[@class="ep-tie-top"]/a[@class="ep-cnum-tie js-tielink js-tiecount JS_NTES_LOG_FE"]/@href')[0]
            return commentUrl


    def getHtmlContentUnicode(self,url):
        # headers={'User-Agent': 'Mozilla/5.0'}
        try:
            request=urllib2.Request(url)
            connection=urllib2.urlopen(request,timeout=5)
            data=connection.read()
            encoding=connection.headers['content-type'].lower().split('charset=')[-1]
            if encoding.lower() == 'text/html':
                encoding = charade.detect(data)['encoding']
            if encoding:
                data = data.decode(encoding=encoding,errors='ignore')
            return data
        except Exception,e:
            print str(e)
            return None

    def extractComments(self,infoStr):
        if not infoStr:
            return None
        infoStr = re.search(self.infoStr_pattern, infoStr)
        if infoStr:
            infoStr = infoStr.group(1)
        try:
            print "infoStr,%s"%infoStr
            dict_obj=json.loads(infoStr)
            comments_list=[]
            for elem in dict_obj['hotPosts']:
                comment_dict={}

                for (k, v) in  elem.items():
                    print k
                    comment_dict[k]={}
                    comment_dict[k]['message']=v['b']
                    if "t" in v.keys():
                        comment_dict[k]['created_at']=v['t']
                    else:
                        comment_dict[k]['created_at']=None
                    comment_dict[k]['author_name']=self.removeformat(v['f'])
                    comment_dict[k]['post_id']=v['p']
                    if "v" in v.keys():
                        comment_dict[k]['up']=v['v']
                    else:
                        comment_dict[k]['up']=None
                    if "a" in v.keys():
                        comment_dict[k]['down']=v['a']
                    else:
                        comment_dict[k]['down']=None
                comments_list.append(comment_dict)

            return comments_list
        except Exception as e:
            print e
            return None

    def removeformat(self, name):
        name=CrawlerUtils.removeUnwantedTag(name)
        name=re.sub("&nbsp;", '', name)
        name=re.sub(ur"[:：]", '', name)
        return name

    def extractupdateTime(self, infoStr):
        if not infoStr:
            return None
        infoStr = re.search(self.infoStr_pattern, infoStr)
        if infoStr:
            infoStr = infoStr.group(1)
        try:
            print "infoStr,%s"%infoStr
            dict_obj=json.loads(infoStr)
            comments_list=[]
            if "thread" in dict_obj.keys():
                return dict_obj["thread"]["ptime"]
            else:
                return None
        except Exception as e:
            print e
            return None


    def parse(self,response):

        items=[]
        itemMetas=[]
        # keyword=self.getKeyword(response)
        #
        # news_blocks=response.xpath('//ul')[0]
        # news_block_items=news_blocks.xpath('./li')
        news_block_items=response.xpath('//div[@class="srg"]/li[@class="g"]')[0]
        news_block_items_ex=[]
        news_block_items_ex.append(news_block_items)
        for news_block_item in news_block_items_ex:
            item=CommentItem()
            item['keyword']=self.keyword
            # print news_block_item.extract()
            print "news_block_item,%s"%news_block_item.extract()
            try:
                sourceUrl=news_block_item.xpath('./div/h3/a/@href').extract()[0]
            except IndexError:
                continue
            # sourceUrl="http://news.163.com/15/0506/02/AOT9E0AL00014AED.html"
            item['_id']=sourceUrl
            item['sourceUrl']=sourceUrl
            # souceUrl="http://news.163.com/15/0506/02/AOT9E0AL00014AED.html"
            commentUrl=self.extractcomment(sourceUrl)
            comments_content=self.getHtmlContentUnicode(commentUrl)
            item['comments']=self.extractComments(comments_content)
            try:
                title = news_block_item.xpath('./div/h3/a/text()').extract()[0]
            except IndexError:
                continue
            titleStr=''.join(title)
            item['title']=titleStr.split('_')[0]
            item['updateTime']=self.extractupdateTime(comments_content)
            source_site=self.source_site
            source_site_name=self.source_site
            item['sourceSiteName']=source_site_name
            item['sourceName']=source_site_name
            item['relateUrl'] = self.relate_url

            # if len(item['content'])>20:
            yield item

        print "****************************************************"

    def GetImgByUrl(self, url):

        apiUrl_img = "http://121.41.75.213:8080/extractors_mvc_war/api/getImg?url="+url

        r_img = requests.get(apiUrl_img)

        imgs = (r_img.json())["imgs"]

        result = {}

        if isinstance(imgs, list) and len(imgs) > 0:

            img_result = self.preCopyImg(url, imgs)

            img_result = self.find_first_img_meet_condition(img_result)

            if img_result is None:
                result['img'] = ''
            else:
                result['img'] = img_result

        else:
            result['img'] = ''

        return result

    def find_first_img_meet_condition(self, img_result):


        for i in img_result:
            if not i.endswith('.gif') and (not 'weima' in i) and (not self.ImgNotMeetCondition(i, 40000)):
                return i

        return ''


    def preCopyImg(self, url, img_urls):

        img_result = []
        for result_i in img_urls:
            if result_i.startswith('/'):
                aa = url.find('/', 7)
                result_i = url[:aa] + result_i
                img_result.append(result_i)

            elif result_i.startswith('..'):
                count = 0
                while result_i.startswith('..'):
                    count += 1
                    result_i = result_i[3:]
                get_list = url.split('/')
                last_list = get_list[2:-1-count]
                result_i = get_list[0] + '//' + '/'.join(last_list) + '/' + result_i
                img_result.append(result_i)

            elif result_i.startswith('.'):
                get_list = url.split('/')
                last_list = get_list[2:-1]
                result_i = get_list[0] + '//' + '/'.join(last_list) + result_i[1:]
                img_result.append(result_i)

            elif re.search(r'^[^http://].*?([\w0-9]*?.jpg)',result_i):
                preurl=re.search(r'(http://.*/)',url)
                if preurl:
                    url_result=preurl.group(1)
                    url_result=url_result+result_i
                    img_result.append(url_result)
            else:
                img_result.append(result_i)

        return img_result




    def GetContentByUrl(self, url):
        apiUrl_text = "http://121.41.75.213:8080/extractors_mvc_war/api/getText?url="
        apiUrl_img = "http://121.41.75.213:8080/extractors_mvc_war/api/getImg?url="

        apiUrl_img += url
        apiUrl_text += url

        r_text = requests.get(apiUrl_text)
        r_img = self.GetImgByUrl(apiUrl_img)

        text = (r_text.json())["text"]
        img = r_img['img']

        result = {}
        result['text'] = text
        result['img'] = img

        return result

    def ImgNotMeetCondition(self, url, size):
        img_url = url

        try:
            file = cStringIO.StringIO(urllib.urlopen(img_url).read())
            im = Image.open(file)
        except IOError:
            print "IOError, imgurl===>", img_url, "url ====>", url
            return True
        width, height = im.size
        print(width, height)
        if width * height < size:
            return True
        print width, "+", height, " url=======>", img_url
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

    def getKeyword(self,response):
        if response==None:
            return None
        print 'initial url is %s'%response._get_url()
        init_url=response._get_url()
        result=urlparse.urlparse(init_url)
        return urlparse.parse_qs(result.query)['word'][0]

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

    def removeNoneSenseRepeated(self,content):
        if content==None:
            return None
        paras=content.split('\n\n')
        # for para in paras:





 