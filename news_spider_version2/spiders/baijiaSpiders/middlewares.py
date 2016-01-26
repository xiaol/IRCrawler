__author__ = 'yangjiwen'
class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "http://201.63.221.137:80"
        print("proxy_start")
