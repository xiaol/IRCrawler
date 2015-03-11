# -*- coding: utf-8 -*-

# Scrapy settings for news_spider_version2 project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'news_spider_version2'

SPIDER_MODULES = ['news_spider_version2.spiders']
NEWSPIDER_MODULE = 'news_spider_version2.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36'

#设置广度优先遍历
DEPTH_PRIORITY =1

SCHEDULER_DISK_QUEUE = 'scrapy.squeue.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeue.FifoMemoryQueue'

#设置遍历深度
DEPTH_LIMIT=4


#存储爬到的item的设置
ITEM_PIPELINES = {'news_spider_version2.pipelines.NewsSpiderVersion2Pipeline':300}

MONGODB_SERVER="h213:27017,h44:27017"
# MONGODB_SERVER="h46:28117,14.17.120.252:27017,121.41.112.241:27017"

MONGODB_REPL='myset'
#
# MONGODB_SERVER ="h46"
# MONGODB_PORT = 28117

# MONGODB_SERVER ="localhost"
# MONGODB_PORT = 27017

MONGODB_DB = "news_ver2"
MONGODB_PRODUCT_COLLECTION="newsProductItems"
MONGODB_COLLECTION = "newsItems"
MONGODB_PARTIAL_ITEM_COLL="partialNewsItem"
MONGODB_CRAWLED_COLLECTION="CrawledItems"
MONGODB_ROOT_INFO_COLL = "rootInfo"
MONGODB_ITEM_TO_ITEM_COLL="itemToItemColl"

# 设置middleware
SPIDER_MIDDLEWARES = {
    'scrapy.contrib.spidermiddleware.offsite.OffsiteMiddleware': 543,
}

# 设置爬取命令
COMMANDS_MODULE='news_spider_version2.commands'

# # 设置redis 连接地址
# REDIS_HOST = '60.28.29.39'
# REDIS_PORT = 6379

# 设置PHANTOM服务地址
PHANTOM_LINK='http://127.0.0.1:8080/wd/hub'

DOWNLOAD_TIMEOUT = 180 #3分钟