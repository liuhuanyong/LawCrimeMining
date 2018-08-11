#!/usr/bin/env python3
# coding: utf-8
# File: crime_law.py.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-8-11
import re
import os



class LawGraph:
    def __init__(self):
        cur = '/'.join(os.path.realpath(__file__).split('/')[:-1])
        self.crimelaw = os.path.join(cur, 'crime_law.txt')

    def build_lawdict(self):
        tuples = []
        cases = [i for i in open(self.crimelaw).read().split('@') if '【' in i and '罪' in i]
        for case in cases:
            datas = self.extract_law(case)
            if datas:
                tuples+=datas
        return tuples

    def extract_law(self, case):
        datas = []
        crime_name = case.split('【')[1].split('】')[0]
        if '罪' not in crime_name or '的' in crime_name:
            return
        if '下列情形之一' not in case.split('】')[1]:
            datas += self.extract_law_2(case, crime_name)
        else:
            tmp = [i.replace('\u3000', '').split('）')[1] for i in case.split('：')[1].split('\n') if '）' in i]
            case = case.replace('下列情形之一，',''.join(tmp)).replace('有下列情形之一的',''.join(tmp)).split('：')[0]
            datas += self.extract_law_2(case, crime_name)
        return datas

    def extract_law_2(self, case, crime_name):
        datas = []
        detail = [i for i in re.split(r'[。；]', case.split('】')[1]) if i and '\n' not in i]
        for i in detail:
            data = {}
            data['crime_name'] = re.split(r'[。；，]', crime_name)
            data['cause'] = re.split(r'[。；，]', i.split('，处')[0])
            data['crime'] = i.split('，处')[-1]
            datas.append(data)
        return datas


handler = LawGraph()
tuples = handler.build_lawdict()
for tuple in tuples:
    print(tuple)