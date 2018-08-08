#!/usr/bin/env python3
# coding: utf-8
# File: lawlib_spider.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-8-8

import urllib.request
from lxml import etree
import pymongo
import re


class LawSpider:
    def __init__(self):
        conn = pymongo.MongoClient()
        self.db = conn['lawsuit']['data2']
        self.db_out = conn['lawsuit']['case']

    '''根据url请求html'''
    def get_html(self, url):
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req)
        html = response.read()
        return html

    '''裁判文书网信息采集'''
    def court_spider(self):
        block_dict = {
                      '北京':'%B1%B1%BE%A9',
                      '天津':'%CC%EC%BD%F2',
                      '河北省':'%BA%D3%B1%B1%CA%A1',
                      '山西省':'%C9%BD%CE%F7%CA%A1',
                      '内蒙古自治区':'%C4%DA%C3%C9%B9%C5%D7%D4%D6%CE%C7%F8',
                      '辽宁省':'%C1%C9%C4%FE%CA%A1',
                      '吉林省':'%BC%AA%C1%D6%CA%A1',
                      '黑龙江省':'%BA%DA%C1%FA%BD%AD%CA%A1',
                      '上海':'%C9%CF%BA%A3',
                      '江苏':'%BD%AD%CB%D5',
                      '浙江':'%D5%E3%BD%AD',
                      '安徽省':'%B0%B2%BB%D5%CA%A1',
                      '福建':'%B8%A3%BD%A8',
                      '江西省':'%BD%AD%CE%F7%CA%A1',
                      '山东省':'%C9%BD%B6%AB%CA%A1',
                      '河南省':'%BA%D3%C4%CF%CA%A1',
                      '湖北省':'%BA%FE%B1%B1%CA%A1',
                      '湖南省':'%BA%FE%C4%CF%CA%A1',
                      '广西壮族自治区':'%B9%E3%CE%F7%D7%B3%D7%E5%D7%D4%D6%CE%C7%F8',
                      '广东':'%B9%E3%B6%AB',
                      '海南省':'%BA%A3%C4%CF%CA%A1',
                      '重庆市':'%D6%D8%C7%EC%CA%D0',
                      '四川省':'%CB%C4%B4%A8%CA%A1',
                      '贵州省':'%B9%F3%D6%DD%CA%A1',
                      '云南省':'%D4%C6%C4%CF%CA%A1',
                      '西藏自治区':'%CE%F7%B2%D8%D7%D4%D6%CE%C7%F8',
                      '陕西省':'%C9%C2%CE%F7%CA%A1',
                      '甘肃省':'%B8%CA%CB%E0%CA%A1',
                      '青海省':'%C7%E0%BA%A3%CA%A1',
                      '宁夏回族自治区':'%C4%FE%CF%C4%BB%D8%D7%E5%D7%D4%D6%CE%C7%F8',
                      '新疆维吾尔自治区':'%D0%C2%BD%AE%CE%AC%CE%E1%B6%FB%D7%D4%D6%CE%C7%F8',
                      '深圳':'%C9%EE%DB%DA'}

        for province, name in block_dict.items():
            max = 70
            self.page_walk(province, name, max)

    '''根据构造的url列表页进行信息采集'''
    def page_walk(self, province, name , max):
        for i in range(max, max+31):
            url = 'http://www.law-lib.com/cpws/cpwsml.asp?bbdw='+name+'&pages='+ str(i) + '&tm1=&tm2='
            try:
                print(url)
                cases = self.extract_cases(url)
                if not cases:
                    continue
                for case in cases:
                    try:
                        data = self.case_parser(case)
                        if data:
                            print(case)
                            data['source'] = province
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
        urls = ['http://www.law-lib.com/cpws/' + i for i in selector.xpath('//span[@class="spanleft"]/a/@href')]
        return urls

    '''根据得到的案件绝对网址，对案件进行请求与页面信息解析'''
    def case_parser(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        title = selector.xpath('//h3[@class="title"]/text()')
        pubtime = selector.xpath('//h2/b/text()')
        content = [i.xpath('string(.)').replace('\xa0','').replace('\t', '') for i in selector.xpath('//div[@class="viewcontent"]')]
        data = {}
        data['url'] = url
        data['title'] = title
        data['pubtime'] = pubtime
        data['content'] = content
        return data

    '''对采集到的文本进行规范化处理'''
    def case_process(self):
        count = 0
        for item in self.db.find():
            count += 1
            print(count)
            if not item['title']:
                continue
            title = item['title'][0].replace('（','(').replace('）',')').replace(' ','').replace('〕',')').replace('〔','(')
            pub = item['pubtime'][0]
            time = pub.split('(')[1].split(')')[0]
            pub_time = self.time_modify(time)
            pub_org = pub.split('(')[0].replace('―', '')
            content = item['content'][0].replace('\u3000','').replace(' ','')
            content = [i for i in re.split('[\r\n]', content) if i not in ['二', '']]
            cate = 'na'
            if '刑事判决书' in content:
                cate = '刑事'
            elif '民事判决书' in content:
                cate = '民事'
            if cate == 'na':
                if '刑' in title and '民' not in title:
                    cate = '刑事'
                else:
                    cate = '民事'
            data = {}
            data['pub_time'] = pub_time
            data['pub_org'] = pub_org
            data['cate'] = cate
            data['title'] = title
            data['content'] = content
            data['url'] = item['url']
            try:
                self.db_out.insert(data)
            except:
                print('duplicated error!!')


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



handler = LawSpider()
handler.case_process()