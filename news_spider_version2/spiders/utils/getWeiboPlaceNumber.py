# #coding=utf-8
# import pprint
# from lxml import etree
# import pymongo
# from pymongo import ReadPreference
# from news_spider_version2.spiders.utils.HttpUtil import get_html
#
# __author__ = 'dengjing'
#
# # con = MongoClient('h46:20010', replicaset='huohuaSet')
# con = pymongo.MongoReplicaSetClient('h37:20010, h7:20010, h46:20010', replicaset='huohuaSet',
#                                         read_preference=ReadPreference.SECONDARY_PREFERRED)
# clct_weiboCityCode = con.monkey.weiboCityCode
#
# def main(url):
#     html = get_html(url)
#     tree = etree.HTML(html)
#     places = tree.xpath('//*//div[@dir="ltr"]/pre')
#     # real_place = {'city': '', 'city_code': ''}
#     real_places = []
#     for place in places:
#         place_strings = place.text
#         place_strings_real = place_strings.split()
#         for place_string_real in place_strings_real:
#             real_place = {}
#             if place_string_real != '' and place_string_real != '\n':
#                 city_string = place_string_real.split(':')
#                 real_place['city'] = city_string[0]
#                 real_place['city_code'] = city_string[1]
#                 real_places.append(real_place)
#     return real_places
#
#
# if __name__ == '__main__':
#     url = 'http://open.weibo.com/wiki/Location/citycode'
#     out_puts = main(url)
#     pprint.pprint(out_puts)
#     for out_put in out_puts:
#         clct_weiboCityCode.insert(out_put, safe=True)
#         # try:
#         #     clct_weiboCityCode.insert(out_put, safe=True)
#         # except:
#         #     continue
