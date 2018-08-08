#!/usr/bin/env python3
# coding: utf-8
# File: crime_spider.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-7-21

import urllib.request
import urllib.parse
from lxml import etree
import re
import pymongo

'''基于司法网的犯罪案件采集'''

class CrimeSpider:
    def __init__(self):
        self.conn = pymongo.MongoClient()
        self.db = self.conn['lawsuit']['crime']
        self.block_dict = {
            '医疗纠纷':['http://www.edu1488.com/article/default.asp?channel=%B0%B8%C0%FD%B4%F3%C8%AB&type1=%D2%BD%C1%C6%BE%C0%B7%D7', 8],
            '国际要案':['http://www.edu1488.com/article/default.asp?channel=%B0%B8%C0%FD%B4%F3%C8%AB&type1=%B9%FA%BC%CA%D2%AA%B0%B8', 4],
            '婚姻继承':['http://www.edu1488.com/article/default.asp?channel=%B0%B8%C0%FD%B4%F3%C8%AB&type1=%BB%E9%D2%F6%BC%CC%B3%D0', 29],
            '消费维权':['http://www.edu1488.com/article/default.asp?channel=%B0%B8%C0%FD%B4%F3%C8%AB&type1=%CF%FB%B7%D1%CE%AC%C8%A8', 16],
            '劳动争议':['http://www.edu1488.com/article/default.asp?channel=%B0%B8%C0%FD%B4%F3%C8%AB&type1=%C0%CD%B6%AF%D5%F9%D2%E9', 78],
            '知识产权':['http://www.edu1488.com/article/default.asp?channel=%B0%B8%C0%FD%B4%F3%C8%AB&type1=%D6%AA%CA%B6%B2%FA%C8%A8', 18],
            '行政案例':['http://www.edu1488.com/article/default.asp?channel=%B0%B8%C0%FD%B4%F3%C8%AB&type1=%D0%D0%D5%FE%B0%B8%C0%FD', 23],
            '刑事案例':['http://www.edu1488.com/article/default.asp?channel=%B0%B8%C0%FD%B4%F3%C8%AB&type1=%D0%CC%CA%C2%B0%B8%C0%FD', 273],
            '民商案例':['http://www.edu1488.com/article/default.asp?channel=%B0%B8%C0%FD%B4%F3%C8%AB&type1=%C3%F1%C9%CC%B0%B8%C0%FD', 167],
        }

    '''构造url请求，请求数据'''
    def get_urls(self, url, channel, type1, page):
        data = {"page": str(page),
                "channel": channel,
                "type1": type1,
                "class": "0",
                "classes": '0',
                "keyword":'',
                'author':'',
                'twosearch':'',
                }
        headers = {
            'Host': 'www.edu1488.com',
            'Connection': 'keep-alive',
            'Content-Length': '117',
            'Cache-Control': 'max-age=0',
            'Origin': 'http://www.edu1488.com',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/66.0.3359.181 Chrome/66.0.3359.181 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'http://www.edu1488.com/article/default.asp',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        data = urllib.parse.urlencode(data).encode('utf-8')
        request = urllib.request.Request(url, headers=headers, data=data)
        response = urllib.request.urlopen(request)
        html = response.read().decode('gbk')
        return html

    '''根据url请求html'''
    def get_html(self, url):
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req)
        html = response.read().decode('gbk')
        return html

    '''url解析'''
    def url_parser(self, content):
        selector = etree.HTML(content)
        urls = ['http://www.edu1488.com' + i for i in  selector.xpath('//a[@class="lmtitle"]/@href')]
        return urls

    '''页面内容解析'''
    def page_parser(self, url, block):
        html = self.get_html(url)
        selector = etree.HTML(html)
        title = selector.xpath('//title/text()')
        if title:
            title = title[0]
        s = [p.xpath('string(.)').replace('\u3000', '').replace('\xa0', '') for p in selector.xpath('//div[@id="text"]')]
        content = ''
        if s:
            text = [i for i in s[0].split('\n') if s]
            content = '\n'.join(text)
        data = {}
        data['url'] = url
        data['category'] = block
        data['title'] = title.replace('-司法考试-中法网学校', '')
        data['content'] = [i.replace(' ','') for i in re.split('[\n\r]', content) if i.replace(' ','').replace('\t','') and '分享到' not in i and '打印文本' not in i and '关闭窗口' not in i and 'js' not in i]
        print(data)
        self.db.insert(data)

    '''采集主函数'''
    def crime_spider(self):
        for block, info in self.block_dict.items():
            url = info[0]
            pages = info[1]
            channel = url.split('channel=')[1].split('&type1=')[0]
            type1 = url.split('&type1=')[1]
            for page in range(pages + 1):
                print(url)
                html = self.get_urls(url, channel, type1, page)
                links = self.url_parser(html)
                if not links:
                    continue
                for link in links:
                    self.page_parser(link, block)


if __name__ == '__main__':
    handler = CrimeSpider()
    handler.crime_spider()