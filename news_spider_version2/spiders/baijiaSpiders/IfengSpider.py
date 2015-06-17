#coding=utf-8
import urllib2
import charade
import requests
import lxml.etree as etree
import scrapy
import re
from news_spider_version2.items import CommentItem
import urlparse
import urllib, cStringIO
import json
from news_spider_version2.spiders.utils.CrawlerUtils import CrawlerUtils
import HTMLParser
import datetime

import time
import random
import socket
import hashlib

# 'scrapy crawl news.baidu.com -a url=' + url_here + ' -a topic=\"'+ topic + '\"'

class IfengSpider(scrapy.Spider):
    name='ifeng.com'
    allowed_domains=['google.com.hk']
    source_site="凤凰新闻"

    def __init__(self, url=None, topic=None, *args, **kwargs):

        super(IfengSpider, self).__init__(*args, **kwargs)
        # keywords = []
        self.start_urls=[]
        topic = topic.split('s')
        self.keyword = "%20".join(topic)
        self.relate_url = url
        print self.keyword, self.relate_url
        # for keyword in keywords:
        # self.start_urls.append('https://www.google.com.hk/?gws_rd=ssl#safe=strict&q=site:163.com++%s'%self.keyword)
        self.start_urls.append('https://www.google.com.hk/search?q=site:ifeng.com++%s&num=100&ie=utf-8&oe=utf-8&aq=t&rls=org.mozilla:en-US:official&client=firefox-a&channel=fflb'%self.keyword)
        # self.start_urls.append('file:///Users/yangjiwen/Documents/xiongjun/GoogleNewsHtml/com++%s.html'%self.keyword)
        for e in self.start_urls:
            print ">>>>>>", e

        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F\][0-9a-fA-F]))+')
        self.time_pattern = re.compile(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}|\d+小时前|\d{4}年\d{2}月\d{2}日 \d{2}:\d{2}')
        self.keyword_pattern = re.compile(r'http://news.baidu.com/ns\?word=(.*?)&.*?')
        self.comment_pattern = re.compile(r'boardId = "(.*?)"')
        self.infoStr_pattern = re.compile(r'replyData=({.*?});', re.DOTALL)
        html_parser = HTMLParser.HTMLParser()
        # url_response=self.getHtmlContentUnicode(self.start_urls[0])
        # print "url_response,%s"%url_response

        # r = requests.get(self.start_urls[0])
        # dom = etree.HTML(r.text)
        # print "r.txt,%s"%r.text





    def extractcomment(self,sourceUrl):

        r = requests.get(sourceUrl)
        dom = etree.HTML(r.text)
        # print "r.txt,%s"%r.text

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
            else:
                commentUrl=""
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
        # infoStr = re.search(self.infoStr_pattern, infoStr)
        # if infoStr:
        #     infoStr = infoStr.group(1)
        try:
            # print "infoStr,%s"%infoStr
            dict_obj=json.loads(infoStr)
            comments_list=[]
            for elem in dict_obj['comments']:
                comment_dict = {}
                comment_dict['1'] = {}
                comment_dict['1']['message'] = CrawlerUtils.removeUnwantedTag(elem['comment_contents'])
                comment_dict['1']['created_at'] = self.convertsecondtoTimestr(int(elem['create_time']))
                comment_dict['1']['author_name'] = elem['uname']
                comment_dict['1']['post_id'] = elem['comment_id']
                comment_dict['1']['up'] = elem['uptimes']
                comment_dict['1']['down'] = int(0)
                comment_dict['1']['author_img_url'] = elem['faceurl']
                comment_dict['1']['type'] = 'ifeng'
                comment_dict['1']['comment_id'] =  self.guid('ifeng')
                comments_list.append(comment_dict)
            return comments_list
        except Exception as e:
            print e
            return None

    def guid(self, *args):
        """
        Generates a universally unique ID.
        Any arguments only create more randomness.
        """
        t = long( time.time() * 1000 )
        r = long( random.random()*100000000000000000L )
        try:
            a = socket.gethostbyname( socket.gethostname() )
        except:
            # if we can't get a network address, just imagine one
            a = random.random()*100000000000000000L
        data = str(t)+' '+str(r)+' '+str(a)+' '+str(args)
        data = hashlib.md5(data).hexdigest()

        return data


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
            # print "infoStr,%s"%infoStr
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
        print "response_body,"
        # print response.body
        print "response_body_end"
        # sourceUrlItem=response.xpath('//div[@class="_I2"]')[0].extract()
        # print "sourceUrlItem,%s"%sourceUrlItem
        try:
            sourceUrl=response.xpath('//div[@class="_I2"]/a/@data-href').extract()[0]
        except IndexError:
            try:
                sourceUrl=response.xpath('//div[@class="_I2"]/h3/a/@href').extract()[0]
            except IndexError:
                # print "extract,%s"%response.xpath('//div[@class="rc"]/h3/a/@href').extract()
                sourceUrl=response.xpath('//div[@class="rc"]/h3/a/@href').extract()[0]


        item=CommentItem()
        item['keyword']=self.keyword
        item['_id']=sourceUrl
        item['sourceUrl']=sourceUrl
        # commentUrl=self.extractcomment(sourceUrl)
        # sourceUrl = 'http://news.ifeng.com/a/20150608/43931984_0.shtml'
        comments_content=self.getHtmlContentUnicode(sourceUrl)
        item['comments']=self.extractComments(comments_content)
        try:
            title = response.xpath('//div[@class="rc"]/h3/a/descendant-or-self::text()').extract()[0]
        except IndexError:
            print "IndexError"


        titleStr=''.join(title)
        item['title'] = titleStr.split('_')[0]
        item['updateTime'] = CrawlerUtils.getDefaultTimeStr()
        source_site_name = self.source_site
        item['sourceSiteName'] = source_site_name
        item['sourceName'] = source_site_name
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



    def getHtmlContentUnicode(self,sourceUrl):
        headers={'User-Agent': 'Mozilla/5.0'}
        try:
            url = 'http://comment.ifeng.com/get?job=1&orderby=uptimes&order=DESC&format=json&pagesize=10'
            values = {'p': str(1), 'docurl': sourceUrl}
            data = urllib.urlencode(values)
            request = urllib2.Request(url, data, headers)
            connection = urllib2.urlopen(request,timeout=50)
            data = connection.read()
            encoding = connection.headers['content-type'].lower().split('charset=')[-1]
            if encoding.lower() == 'text/html':
                encoding = charade.detect(data)['encoding']
            # if encoding.lower()=='gb2312':
            #     encoding='gbk'
            if encoding:
                data = data.decode(encoding=encoding, errors='ignore')
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

    def convertsecondtoTimestr(self, time):
        format='%Y-%m-%d %H:%M:%S'
        # starttime=datetime.datetime(1970,1,1)
        starttime=datetime.datetime(1970, 1, 1, 8, 0)
        timeDelta=datetime.timedelta(milliseconds=time*1000)
        defaultTime=starttime+timeDelta
        defaultTimestr=defaultTime.strftime(format)
        return defaultTimestr



 