#coding=utf-8
import re

__author__ = 'galois'
test_str1=u'<section class="tn-Powered-by-XIUMI" style="box-sizing: border-box;">应 @别业居幽处 邀，补答案</section><section class="tn-Powered-by-XIUMI" style="box-sizing: border-box;"><br class="tn-Powered-by-XIUMI" style="box-sizing: border-box;"></section>'
regex_pat1=re.compile('<section(?: [^<>]+?)? class="tn-Powered-by-XIUMI"(?: [^<>]+?)?>.*?</section>')

for elem in re.findall(regex_pat1,test_str1):
    print "elem is %s"%elem


