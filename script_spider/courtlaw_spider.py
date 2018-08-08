#!/usr/bin/env python3
# coding: utf-8
# File: law_spider.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-8-7

import urllib.request
from lxml import etree
import pymongo

'''最高人民法院裁判文书网采集'''

class LawSpider:
    def __init__(self):
        conn = pymongo.MongoClient()
        self.db = conn['lawsuit']['data']

    '''根据url请求html'''
    def get_html(self, url):
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req)
        html = response.read().decode('utf-8')
        return html

    '''裁判文书网信息采集'''
    def court_spider(self):
        block_dict = {
                      '民事案件': [2, 596],
                      '刑事案件':[1, 41],
                      '行政案件': [3, 76],
                      '知识产权': [6, 64],
                      '赔偿案件': [4, 17],
                      '执行案件': [5, 16],
                      }
        for block, info in block_dict.items():
            id = info[0]
            max = info[1]
            self.page_walk(block, id, max)

    '''根据构造的url列表页进行信息采集'''
    def page_walk(self, block, id , max):
        for i in range(1, max+1):
            url = 'http://www.court.gov.cn/wenshu/gengduo-{0}.html?page={1}'.format(id, i)
            try:
                print(url)
                cases = self.extract_cases(url)
                if not cases:
                    continue
                for case in cases:
                    try:
                        data = self.case_parser(block, case)
                        if data:
                            try:
                                self.db.insert(data)
                            except Exception as e:
                                print(e)
                                print('duplicated...')
                    except:
                        pass
            except:
                pass
        return

    '''根据页面，解析出对应的案件url'''
    def extract_cases(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        urls = ['http://www.court.gov.cn' + i for i in selector.xpath('//li[@class="list_tit"]/a/@href')]
        return urls

    '''根据得到的案件绝对网址，对案件进行请求与页面信息解析'''
    def case_parser(self, block, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        title = selector.xpath('//title/text()')
        pubtime = selector.xpath('//li[@class="fl print"]/text()')[0].replace('发布时间：', '')
        content = [i.xpath('string(.)').replace('\xa0','').replace('\t', '') for i in selector.xpath('//div[@class="txt_txt"]/div')]
        if not title:
            pass
        title = title[0].replace('（', '(').replace('）', ')').replace(' ', '').replace('〕', ')').replace('〔','(')
        title = title.replace('-裁判文书-中华人民共和国最高人民法院', '')
        pub = pubtime
        pub_time = self.time_modify(pub)
        pub_org = ''
        content = content
        content = [i.replace('\n', '').replace('\r', '').replace(' ', '').replace('\u3000', '') for i in content if
                   '{' not in i and i.replace('\n', '').replace('\r', '').replace(' ', '')]
        cate = block.replace('案件', '')
        data = {}
        data['pub_time'] = pub_time
        data['pub_org'] = pub_org
        data['cate'] = cate
        data['title'] = title
        data['content'] = content
        data['url'] = url
        return data

    '''规范化时间表示'''
    def time_modify(self, time):
        year = time.split('-')[0]
        month = time.split('-')[1]
        day = time.split('-')[2]
        if int(month) < 10 and len(month) < 2:
            month = '0' + month

        if int(day) < 10 and len(day) < 2:
            day = '0' + day

        return '-'.join([year, month, day])


if __name__ == "__main__":
    handler = LawSpider()
    handler.court_spider()