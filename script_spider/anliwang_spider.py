#!/usr/bin/env python3
# coding: utf-8
# File: anliwang.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-7-21

import urllib.request
import urllib.parse
from lxml import etree
import pymongo
import re

'''基于司法网的犯罪案件采集'''
class CrimeSpider:
    def __init__(self):
        self.conn = pymongo.MongoClient()
        self.db = self.conn['lawsuit']['crime']
        self.block_dict = {
            '刑事':['http://www.anliguan.com/news/xinshi/list_4_',3364],
            '民事':['http://www.anliguan.com/news/minfa/list_3_',2004],
            '诈骗':['http://www.anliguan.com/news/zhapian/list_18_',1594],
            '传销':['http://www.anliguan.com/news/chuanxiao/list_8_',158]
        }

    '''根据url，请求html'''
    def get_html(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/51.0.2704.63 Safari/537.36'}
        req = urllib.request.Request(url=url, headers=headers)
        res = urllib.request.urlopen(req)
        html = res.read().decode('utf-8')
        return html

    '''url解析'''
    def url_parser(self, content):
        selector = etree.HTML(content)
        urls = ['http://www.anliguan.com' + i for i in  selector.xpath('//h2[@class="item-title"]/a/@href')]
        return urls

    '''正文解析'''
    def page_parse(self, url, block):
        content = self.get_html(url)
        selector = etree.HTML(content)
        title = selector.xpath('//title/text()')
        print(title, url)
        if title:
            title = title[0].replace('\u3000','').split('_')[0]
        s = [p.xpath('string(.)').replace('\u3000', '').replace('\xa0', '') for p in selector.xpath('//div[@class="entry-content clearfix"]')]
        content = ''
        if s:
            content =  s[0].split('/*6:5 创建于')[0]
        if title and content:
            data = {}
            data['url'] = url
            data['category'] = block
            data['title'] = title
            data['content'] = [i.replace(' ', '').replace('\t','') for i in re.split('[\n\r]', content) if
                               i.replace(' ', '').replace('\t','')]
            print(data)
            self.db.insert(data)

    '''采集主函数'''
    def crime_spider(self):
        for block, info in self.block_dict.items():
            url = info[0]
            pages = info[1]
            for page in range(1, pages + 1):
                url_ = url + '%s.php' % page
                print(url_)
                html = self.get_html(url_)
                links = self.url_parser(html)
                if not links:
                    continue
                for link in links:
                    self.page_parse(link, block)

if __name__ == '__main__':
    handler = CrimeSpider()
    handler.crime_spider()