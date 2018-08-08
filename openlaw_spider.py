#!/usr/bin/env python3
# coding: utf-8
# File: law2_spider.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-8-7

import pymongo
from lxml import etree
import requests
import time

class LawSpider:
    def __init__(self):
        conn = pymongo.MongoClient('192.168.1.37', 27017)
        self.db = conn['lawsuit']['data2']

    '''根据url请求html'''
    def get_html(self, url):
        full = 'http://192.168.1.236:8050/render.html?url={0}&timeout=10&wait=1'.format(url)
        req = requests.get(full)
        html = req.text
        return html

    '''裁判文书网信息采集'''
    def court_spider(self):
        block_dict = [
                        ['8df0903dfdb74937a9ebb39ab95f5b0a','人格权纠纷','民事'],
                        ['a3ea79cf193f4e07a27a900e29585dbb','婚姻家庭、继承纠纷','民事'],
                        ['e4de58bfcc6e47e0a0d7ce89c1f00fbd','物权纠纷','民事'],
                        ['108a9c0963df47518f2ec600148c6182','合同、无因管理、不当得利纠纷','民事'],
                        ['d8347b89678645e1887045b4200e822f','知识产权与竞争纠纷','民事'],
                        ['44f522e92013462abc4ad7049ebd9e3e','劳动争议、人事争议','民事'],
                        ['91a7892e8b574d2e8641284c138f037f','海事海商纠纷','民事'],
                        ['21dcbfbcdfa74a44b179c6931a4df58f','与公司、证券、保险、票据等有关的民事纠纷','民事'],
                        ['08df5355fffa4053b9f4478a46cd51d2','侵权责任纠纷','民事'],
                        ['115bede07bcd466ea72421b1de5d427d','适用特殊程序案件案由','民事'],
                        ['d342bfa455a4451e9e547a893e83060f','行政管理范围','行政'],
                        ['2777655f16b3400a92f0a64ff1d71de1','行政行为种类','行政'],
                        ['4815e07513704d8f9db48e1127c0cde6','刑事赔偿','赔偿'],
                        ['00d826d4545e4d0d8521a9f41f8ad6e8','非刑事赔偿','赔偿'],
                        ['f9c7f66451834eaca2c8aff4fcc20861','危害国家安全','刑事'],
                        ['5f3f9a95d39d4d1fb2c5ea52dd6a6cd0','危害公共安全','刑事'],
                        ['cb135398bcb445c3a5ec87341b3245a0','破坏社会主义市场经济秩序','刑事'],
                        ['d8a5ae548bfc4d31b36eda610628369e','侵犯公民人身权利、民主权利','刑事'],
                        ['0be8a7aee2f848d288499b2a7396de43','侵犯财产','刑事'],
                        ['b60985d13ebb40bd8336702a2aa3a65d','妨害社会管理秩序','刑事'],
                        ['391c916bc5434103a2b996b8220a25ba','危害国防利益','刑事'],
                        ['3deb56e97c6e428b81c754a0a82ea618','贪污贿赂','刑事'],
                        ['afe9f07757144214bd514d1c178c15ce','渎职','刑事'],
                        ['82d2ad11b41a46cea74310566e624819','军人违反职责','刑事']
                    ]

        for info in block_dict:
            id = info[0]
            subtype = info[1]
            bigtype = info[2]
            max = 50
            try:
                self.page_walk(bigtype, subtype, id, max)
            except:
                pass

    '''根据构造的url列表页进行信息采集'''
    def page_walk(self, bigtype, subtype, id , max):
        for i in range(1, max+1):
            url = 'http://openlaw.cn/search/judgement/type?causeId={0}&page={1}'.format(id, i)
            time.sleep(3)
            print(url)
            cases = self.extract_cases(url)
            if not cases:
                continue
            for case in cases:
                try:
                    time.sleep(3)
                    self.case_parser(case, bigtype, subtype)
                except:
                    pass
        return

    '''根据页面，解析出对应的案件url'''
    def extract_cases(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        urls = ['http://openlaw.cn' + i for i in selector.xpath('//h3[@class="entry-title"]/a/@href')]
        return urls

    '''根据得到的案件绝对网址，对案件进行请求与页面信息解析'''
    def case_parser(self, url, bigtype, subtype):
        html = self.get_html(url)
        selector = etree.HTML(html)
        title = selector.xpath('//title/text()')[0].split('裁判文书')
        pubtime = selector.xpath('//li[@class="ht-kb-em-date"]/text()')
        author = selector.xpath('//li[@class="ht-kb-em-author"]/a/text()')
        category = selector.xpath('//li[@class="ht-kb-em-category"]/text()')
        litigant = [i.xpath('string(.)') for i in selector.xpath('//div[@id="Litigants"]')]
        explain = [i.xpath('string(.)') for i in selector.xpath('//div[@id="Explain"]')]
        procedure = [i.xpath('string(.)') for i in selector.xpath('//div[@id="Procedure"]')]
        opinion = [i.xpath('string(.)') for i in selector.xpath('//div[@id="Opinion"]')]
        verdict = [i.xpath('string(.)') for i in selector.xpath('//div[@id="Verdict"]')]
        inform = [i.xpath('string(.)') for i in selector.xpath('//div[@id="Inform"]')]
        ending = [i.xpath('string(.)') for i in selector.xpath('//div[@id="Ending"]')]
        data = {}
        data['bigtype'] = bigtype
        data['subtype'] = subtype
        data['title'] = ''.join(title)
        data['pubtime'] = ''.join(pubtime)
        data['author'] = ''.join(author)
        data['category'] = ''.join(category)
        data['litigant'] = ''.join(litigant)
        data['explain'] = ''.join(explain)
        data['procedure'] = ''.join(procedure)
        data['opinion'] = ''.join(opinion)
        data['verdict'] = ''.join(verdict)
        data['inform'] = ''.join(inform)
        data['ending'] = ''.join(ending)
        data['url'] = url
        if data:
            try:
                self.db.insert(data)
                print(url)
            except:
                print('duplicated record...')


if __name__ == '__main__':
    handler = LawSpider()
    handler.court_spider()
