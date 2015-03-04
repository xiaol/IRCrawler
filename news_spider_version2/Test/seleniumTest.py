__author__ = 'galois'
#coding: utf-8
import sys

from selenium import webdriver

def main(url):
    caps={
        'takeScreenshot':False,
        'javascriptEnabled':True,
    }

    phantom_link='http://127.0.0.1:8080/wd/hub'

    driver=webdriver.Remote(
        command_executor=phantom_link,
        desired_capabilities=caps
    )

    driver.get(url)

    print driver.title
    elems=driver.find_elements_by_xpath('//*[@id="sogou_vr_11002601_box_0"]/div[@class="img_box2"]/a')
    for elem in elems:
        print elem.get_attribute('href')


if __name__=="__main__":
    url='http://weixin.sogou.com/gzh?openid=oIWsFt5HJEgGlbxXAB2hBcmwjQho'
    main(url)