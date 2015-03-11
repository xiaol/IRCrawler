#coding=utf-8
import hashlib
import urllib2
import charade
from scrapy.utils.url import canonicalize_url

__author__ = 'galois'

import re
import datetime
import sys
import HTMLParser
reload(sys) # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')

class CrawlerUtils:


    SPACES_PATTERN=re.compile(ur'^[\s\xa0\u3000]*$')
    SPECIAL_SPACE=re.compile(ur'[\xa0\s]*')
    Q_space=unichr(12288)
    img_src_pattern=re.compile(r'<img(?: .*?)? src="(.*?)"')

    #用来转换时间格式的
    timeReg=re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
    timeReg2=re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2})")
    timeReg3=re.compile(r"(\d{2}/\d{2} \d{2}:\d{2})")
    timeReg4=re.compile(r"(\d{4}-\d+-\d+ \d{2}:\d{2})")
    timeReg5=re.compile(ur'(\d{4}[\u4e00-\u9fa5]\d+[\u4e00-\u9fa5]\d+[\u4e00-\u9fa5] \d{2}:\d{2})')
    timeReg6=re.compile(ur"(\d{4}[\u4e00-\u9fa5]\d+[\u4e00-\u9fa5]\d+)")
    timeReg7=re.compile(r'(\d{4}-\d+-\d+ \d+:\d+:\d+)')

    tagPatBegin=re.compile(r'(\s*)((?:<p>)|(?:<p .*?>))(\s*)')
    tagPatEnd=re.compile(r'(?:</p>)|(?:<br>)')
    tagPatDel=re.compile(r'<.*?>',re.DOTALL)

    paragraph_Pat=re.compile(r'(?:(?:<p>)|(?:<p .*?>))(.*?)</p>',re.DOTALL)

    scriptPat=re.compile(r'(?:(?:<script>)|(?:<script .*?>)).*?</script>',re.DOTALL)
    stylePat=re.compile(r'((?:<style>)|(?:<style .*?>)).*?</style>',re.DOTALL)
    parasedPat=re.compile(r'<!--(.*?)-->',re.DOTALL)

    urlPattern=re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    html_parser = HTMLParser.HTMLParser()


    category_map={'news':'新闻', '资讯':'新闻',\
    'tech':'科技', \
    'war':'军事', \
'sports':'体育', \
'ent': '娱乐' , \
'iwf':'足球',\
'money':'财经',\
'auto':'汽车',\
'mobile':'手机',\
'digi':'数码',\
'hea':'家电',\
# 'gz':'广州房产',\
'gz':'房产',\
'ad':'商讯',\
'lady':'女人',\
'jiu':'酒',\
'jiankang':'健康',\
'zx':'彩票',\
'fashion':'时尚',\
'edu':'教育',\
'discovery':'探索',\
# 'sh':'上海房产', \
'sh':'房产', \
'book':'读书',\
'daxue':'大学',\
'gov':'政务',\
'home':'家居',\
'travel':'旅游',\
# 'bj':'北京房产',\
'bj':'房产',\
# 'sz':'深圳房产',\
'sz':'房产',\
'gongyi':'公益',\
'vhouse':'海外',\
'world':'国际',\
'baby':'亲子',\
'game':'游戏',\
'run':'跑步',\
'中国财经':'财经',\
'国际财经':'财经',\
'金融':'财经',\
'新闻中心':'新闻'}

    site_info=['凤凰','网易','新浪']

    @classmethod
    def extractImgUrl(cls,content):
        if content==None:
            return None
        matcher=cls.img_src_pattern.search(content)
        if matcher:
            imgSrc=matcher.group(1)
            if imgSrc.endswith('.gif'):
                return None
            return imgSrc
        return None

    @classmethod
    def formatTime(cls,timeStr):
        format='%Y-%m-%d %H:%M:%S'
        timeDelta=datetime.timedelta(milliseconds=3600*1000)
        defaultTime=(datetime.datetime.now()-timeDelta)
        defaultTimeStr=defaultTime.strftime(format)
        if timeStr==None:
            return defaultTimeStr
        m=cls.timeReg.search(timeStr)
        if m:
            return m.group(1)
        m=cls.timeReg2.match(timeStr)
        if m:
            return m.group(1)+":"+defaultTimeStr.split(":")[2]
        m=cls.timeReg3.match(timeStr)
        if m:
            month_to_minute=m.group(1).replace("/","-")
            year=defaultTimeStr.split("-")[0]
            return year+"-"+month_to_minute+":"+defaultTimeStr.split(":")[2]
        m=cls.timeReg4.match(timeStr)
        if m:
            orgTimeStr= m.group(1)
            times=re.split(r'\s',orgTimeStr)
            year_to_day=times[0]
            hour_to_minute=times[1]
            year_to_day_arr=year_to_day.split('-')
            year_to_dayStr=cls.makeYearToDay(year_to_day_arr[0],year_to_day_arr[1],year_to_day_arr[2])

            return year_to_dayStr+' '+hour_to_minute+':'+defaultTimeStr.split(':')[2]
        m=cls.timeReg5.match(timeStr.decode('utf8'))
        if m:
            orgTimeStr=m.group(1)
            times=re.split(r'\s',orgTimeStr)
            year_to_day_arr=re.split(ur'[-\u4e00-\u9fa5]',times[0])
            year_to_dayStr=cls.makeYearToDay(year_to_day_arr[0],year_to_day_arr[1],year_to_day_arr[2])
            return year_to_dayStr+' '+times[1]+':'+defaultTimeStr.split(':')[2]

        m=cls.timeReg6.match(timeStr.decode('utf8'))
        if m:
            orgTimeStr=m.group(1)
            times=re.split(r'\s',orgTimeStr)
            year_to_day_arr=re.split(ur'[-\u4e00-\u9fa5]',times[0])
            year_to_dayStr=cls.makeYearToDay(year_to_day_arr[0],year_to_day_arr[1],year_to_day_arr[2])
            return year_to_dayStr+' '+re.split(r'\s',defaultTimeStr)[1]
        m=cls.timeReg7.search(timeStr.decode('utf8'))
        if m:
            orgTimeStr=m.group(1)
            times=re.split(r'\s',orgTimeStr)
            year_to_day_arr=re.split(r'-',times[0])
            hour_to_second_arr=re.split(r':',times[1])
            year_to_dayStr=cls.makeYearToDay(year_to_day_arr[0],year_to_day_arr[1],year_to_day_arr[2])
            hour_to_second_str=cls.makeHourToSecond(hour_to_second_arr[0],hour_to_second_arr[1],hour_to_second_arr[2])
            return year_to_dayStr+' '+hour_to_second_str

        return defaultTimeStr

    @classmethod
    def makeYearToDay(cls,year,month,day):
        timeList=[]
        timeList.append(year)
        timeList.append('-')
        if len(month)<2:
            timeList.append('0');
        timeList.append(month)
        timeList.append('-')
        if(len(day)<2):
            timeList.append('0')
        timeList.append(day)

        return ''.join(timeList)

    @classmethod
    def makeHourToSecond(cls,hour,minitue,second):
        timeList=[]
        if len(hour)<2:
            timeList.append('0');
        timeList.append(hour)
        timeList.append(':')
        if len(minitue)<2:
            timeList.append('0')
        timeList.append(minitue)
        timeList.append(':')
        if len(second)<2:
            timeList.append('0')
        timeList.append(second)
        return ''.join(timeList)

    """
    根据tag来确定替换的字符比 <p .*?> 该替换为‘\t'
    </p> 替换为'\n'
    其它直接替换为‘’
    """
    # @classmethod
    # def removeTag(cls,content):
    #     if content==None:
    #         return None
    #     result=re.sub(cls.tagPatBegin,'\t\t',content)
    #     result=result.replace('\n','')
    #     result=re.sub(cls.tagPatEnd,'\n',result)
    #     result=re.sub(cls.tagPatDel,'',result)
    #     return '\t\t'+result.strip()

    @classmethod
    def removeTag(cls,content):
        if content==None:
            return None
        result=content
        result=cls.removeScript(result)
        result=result.replace('\n','')
        result=result.replace('\r','')
        result=re.sub(cls.tagPatBegin,'',result)
        result=re.sub(cls.tagPatEnd,'\n',result)
        result=re.sub(cls.tagPatDel,'',result)
        resultArr=result.split('\n')
        resultList=[]
        for elem in resultArr:
            elem=elem.replace(u'\xa0','')
            if (not cls.isAllSpaces(elem))& (not cls.isPagesInfo(elem)):
                elem=elem.strip()
                elem=cls.Q_space+cls.Q_space+elem+'\n\n'
                resultList.append(elem)
        return ''.join(resultList).rstrip()

    def isDelete(self,tagContent):
        if tagContent==None:
            return True

        pattern=re.compile(r'(?:</?p>)|(?:<p .*?>)')
        if pattern.match(tagContent):
            return False
        imgSrcPattern=re.compile(r'<img src="(.*?)".*?>')
        matcher=imgSrcPattern.match(tagContent)

        if matcher:
            imgUrl=matcher.group(1)
            if imgUrl.endswith('.gif'):
                return True
            else:
                return False

        return True

    '''
    根据去除script标签以及style 块里面的文字
    '''

    @classmethod
    def removeScript(cls,content):
        if content==None:
            return None
        return re.sub(cls.scriptPat,'',content)

    @classmethod
    def removeStyle(cls,content):
        if content==None:
            return None
        return re.sub(cls.stylePat,'',content)

    @classmethod
    def removeUnwantedTag(cls,content):
        if content==None:
            return None
        return re.sub(cls.tagPatDel,'',content)

    @classmethod
    def map_to_Category(cls,rawCategory):
        if rawCategory:
            category=rawCategory
            for elem in cls.site_info:
                category=category.replace(elem,'')
            if cls.category_map.__contains__(category):
                category=cls.category_map.get(category)
            return category
        return None

    @classmethod
    def isUrl(cls,test_str):
        if test_str:
            result=cls.urlPattern.match(test_str)
            if result:
                return True
        return False

    @classmethod
    def spaceB2Q(cls,ustring):
        """半角空格转全角"""
        return ustring.replace(' ',cls.Q_space)

    @classmethod
    def isAllSpaces(cls,test_str):
        if test_str==None:
            return True
        # test_str=unicode(test_str)
        if re.match(cls.SPACES_PATTERN,test_str.decode(errors='ignore')):
            return True
        return False

    @classmethod
    def extractContentFromRaw(cls,content):
        if content==None:
            return None
        contentList=[]
        for para in re.findall(cls.paragraph_Pat,content):
            # print "raw para is %s"%para
            result=para
            result=cls.removeParasedCode(result)
            result=cls.removeScript(result)

            # print "removeScript para is %s"%result
            result=cls.removeStyle(result)
            result=re.sub(cls.tagPatDel,'',result)
            result=result.strip()
            if (not cls.isAllSpaces(result)) & (not cls.isPagesInfo(result)):
                result=cls.Q_space+cls.Q_space+result+'\n\n'
                contentList.append(result)
        contentResult=''.join(contentList)
        contentResult=contentResult.rstrip()
        return contentResult

    @classmethod
    def removeParasedCode(cls,content):
        if content==None:
            return None
        return re.sub(cls.parasedPat,'',content)

    @classmethod
    def getDefaultTimeStr(cls):
        format='%Y-%m-%d %H:%M:%S'
        timeDelta=datetime.timedelta(milliseconds=3600*1000)
        defaultTime=(datetime.datetime.now()-timeDelta)
        defaultTimeStr=defaultTime.strftime(format)
        return defaultTimeStr

    @classmethod
    def isPagesInfo(cls,para):
        para=para.strip()
        paraArr=re.split(r'\s',para)
        pageInfos=['上一页','下一页']
        digitalCount=0
        pageInfoCount=0
        for elem in paraArr:
            if elem.isdigit():
                digitalCount=digitalCount+1
            elif elem in pageInfos:
                pageInfoCount=pageInfoCount+1
        if digitalCount>3:
            return True
        if digitalCount>1 & pageInfoCount>0:
            return True
        return False

    @classmethod
    def splitSpaces(cls,input_str):
        if None==input_str:
            return None
        return re.split(cls.SPECIAL_SPACE,input_str.decode('utf-8'))

    @classmethod
    def make_img_text_pair(cls,listInfos):
        img_text_infos=[]
        if None==listInfos:
            return None
        imgBefore=True
        img_text_elem=[]
        for elem in listInfos:
            if imgBefore:
                if 'txt' in elem:
                    img_text_elem.append(elem)
                    img_text_infos.append(img_text_elem)
                    imgBefore=False
                else:
                    if len(img_text_elem):
                        img_text_infos.append(img_text_elem)
                    img_text_elem=[]
                    img_text_elem.append(elem)
            else:
                img_text_elem=[]
                if 'txt' in elem:
                    img_text_elem.append(elem)
                    img_text_infos.append(img_text_elem)
                else:
                    img_text_elem.append(elem)
                    imgBefore=True
        if imgBefore & len(img_text_elem):
            img_text_infos.append(img_text_elem)
        return img_text_infos

    @classmethod
    def getHtmlContentUnicode(cls,url):
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

    @classmethod
    def extractContent(cls,rawContent,content_pat,img_pat,para_pat,base_url=None,filt_imgs=None):
        listInfos=[]

        for line in re.findall(content_pat,rawContent):
            imgSearch=re.search(img_pat,line)
            if imgSearch:
                img_url=imgSearch.group(1)
                if base_url!=None:
                    img_url=base_url+img_url
                listInfos.append({'img':img_url})
                # print "img is: %s" %img_url
            else:
                txtSearch=re.search(para_pat,line)
                if txtSearch:
                    result=None
                    groups=txtSearch.groups()
                    for group in groups:
                        if group:
                            result=group
                            break
                    if None==result:
                        continue

                    result=CrawlerUtils.removeParasedCode(result)
                    result=CrawlerUtils.removeScript(result)
                    result=CrawlerUtils.removeUnwantedTag(result)
                    result=cls.html_parser.unescape(result)
                    if (not CrawlerUtils.isAllSpaces(result)) & (not CrawlerUtils.isPagesInfo(result)):
                        result=CrawlerUtils.Q_space+CrawlerUtils.Q_space+result.strip()+'\n\n'
                        # print "txt is :%s" %result
                        listInfos.append({'txt':result})
        return CrawlerUtils.make_img_text_pair(listInfos)

    @classmethod
    def extractContentDelUnwantedPat(cls,rawContent,content_pat,img_pat,para_pat,unwanted_pat):
        listInfos=[]

        for line in re.findall(content_pat,rawContent):
            imgSearch=re.search(img_pat,line)
            if imgSearch:
                listInfos.append({'img':imgSearch.group(1)})
                # print "img is %s" %imgSearch.group(1)
            else:
                line=cls.html_parser.unescape(line)
                txtSearch=re.search(para_pat,line)
                if txtSearch:
                    result=txtSearch.group(1)
                    result=CrawlerUtils.removeParasedCode(result)
                    result=CrawlerUtils.removeScript(result)
                    result=CrawlerUtils.removeUnwantedTag(result)
                    if (not CrawlerUtils.isAllSpaces(result)) & (not CrawlerUtils.isPagesInfo(result)):
                        result=result.strip()
                        if result.startswith(unwanted_pat):
                            continue
                        result=CrawlerUtils.Q_space+CrawlerUtils.Q_space+result+'\n\n'
                        # print "txt is :%s" %result
                        listInfos.append({'txt':result})
        return CrawlerUtils.make_img_text_pair(listInfos)

    @classmethod
    def extractContentImgTxtMixture(cls,rawContent,content_pat,img_pat,para_pat,base_url=None,filt_imgs=None):
        listInfos=[]

        for line in re.findall(content_pat,rawContent):
            for img in re.findall(img_pat,line):
                img_url=img
                if base_url!=None:
                    img_url=base_url+img_url
                if None==filt_imgs:
                    listInfos.append({'img':img_url})
                    # print "img is %s" %img_url
                elif not img_url in filt_imgs:
                    listInfos.append({'img':img_url})
                    # print "img is %s" %img_url

            txtSearch=re.search(para_pat,line)
            if txtSearch:
                groups=txtSearch.groups()
                for group in groups:
                    if group:
                        result=group
                        break
                if None==result:
                    continue
                result=CrawlerUtils.removeParasedCode(result)
                result=CrawlerUtils.removeScript(result)
                result=CrawlerUtils.removeUnwantedTag(result)
                result=cls.html_parser.unescape(result)
                if (not CrawlerUtils.isAllSpaces(result)) & (not CrawlerUtils.isPagesInfo(result)):
                    result=CrawlerUtils.Q_space+CrawlerUtils.Q_space+result.strip()+'\n\n'
                    # print "txt is :%s" %result
                    listInfos.append({'txt':result})
        result=CrawlerUtils.make_img_text_pair(listInfos)
        return result
    @classmethod
    def generateId(cls,url):
        fp = hashlib.sha1()
        fp.update(canonicalize_url(url))
        return fp.hexdigest()

    @classmethod
    def extractImgUrl(cls,rawContent,content_pat,img_pat,base_url=None,filt_imgs=None):

        for line in re.findall(content_pat,rawContent):
            for img in re.findall(img_pat,line):
                img_url=img
                if base_url!=None:
                    img_url=base_url+img_url
                if None==filt_imgs:
                    return img_url
                elif not img_url in filt_imgs:
                    return img_url
        return None