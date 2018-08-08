#!/usr/bin/env python3
# coding: utf-8
# File: export_data.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-8-8

import pymongo

class LawSpider:
    def __init__(self):
        conn = pymongo.MongoClient()
        self.db = conn['lawsuit']['case']
        self.db_crime = conn['lawsuit']['crime']

    '''导出判决数据'''
    def export_data(self):
        i = 0
        for item in self.db.find({'cate':'刑事'}).limit(500):
            i += 1
            title = item['title']
            pubtime = item['pub_time']
            cate = item['cate']
            content = '\n'.join(item['content'])
            f = open('corpus_lawsuit/%s.txt'%i, 'w+')
            f.write('category:' + cate + '\n')
            f.write('title:' + title +'\n')
            f.write('publictime:'+ pubtime + '\n')
            f.write('content:' + content + '\n')
            f.close()

        for item in self.db.find({'cate':'民事'}).limit(500):
            i += 1
            title = item['title']
            pubtime = item['pub_time']
            cate = item['cate']
            content = '\n'.join(item['content'])
            f = open('corpus_lawsuit/%s.txt'%i, 'w+')
            f.write('category:' + cate + '\n')
            f.write('title:' + title +'\n')
            f.write('publictime:'+ pubtime + '\n')
            f.write('content:' + content + '\n')
            f.close()
        return

    '''导出犯罪数据'''
    def export_data_crime(self):
        i = 0
        for item in self.db_crime.find().limit(1000):
            i += 1
            title = item['title']
            cate = item['category']
            content = '\n'.join(item['content'])
            f = open('corpus_crime/%s.txt' % i, 'w+')
            f.write('category:' + cate + '\n')
            f.write('title:' + title + '\n')
            f.write('content:' + content + '\n')
            f.close()
        return




handler = LawSpider()
handler.export_data_crime()