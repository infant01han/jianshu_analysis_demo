# -*- coding: utf-8 -*-
# @Time    : 2020/4/9 0009 8:50
# @Author  : Han lei
# @Email   : hanlei5012@163.com
# @File    : jianshu_dynamic_spider.py
# @Software: PyCharm
import sys
import time
from pprint import pprint

import pymongo
import requests
from fake_useragent import UserAgent
from lxml import etree
sys.setrecursionlimit(6000) #设置这个可以突破递归限制

class JianshuSpider:
    def __init__(self,slug):
        self.slug=slug
        self.client=pymongo.MongoClient(host='localhost')
        self.db=self.client['JianShu2']
        self.BASE_HEADERS= {
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
            'Host': 'www.jianshu.com',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'text/html, */*; q=0.01',
            'User-Agent': UserAgent().random,
            'Connection': 'keep-alive',
            'Referer': 'http://www.jianshu.com',
        }
        # 初始化盛数据的容器：timeline
        self.timeline={
            'comment_note': [],
            'like_note': [],
            'reward_note': [],
            'share_note': [],
            'like_user': [],  # 用户id
            'like_collection': [],  # 专题id
            'like_comment': [],
            'like_notebook': [],  # 文集id
            'reward_user':[]
        }
        self.lastest_time = ''

    def get_user_timeline(self, maxid, page):
        print(f'正在抓取第{page}页动态')
        AJAX_HEADERS = {"Referer": "http//:www.jianshu.com/u/{slug}".format(slug=self.slug),
                        "X-PJAX": "true"}
        headers = dict(self.BASE_HEADERS, **AJAX_HEADERS)
        if maxid == None:
            url = f'https://www.jianshu.com/users/{self.slug}/timeline'
        else:
            url = f'https://www.jianshu.com/users/{self.slug}/timeline?max_id={maxid}&page={page}'
        rsp = requests.get(url, headers=headers)
        # print(rsp.text)
        tree = etree.HTML(rsp.text)  # 将回应变成xml的树，可以用xpath解析
        lis = tree.xpath('.//li')
        last_li_id = lis[-1].xpath('@id')[0].replace('feed-', '')
        print(last_li_id)
        maxid = int(last_li_id) - 1
        print(len(lis))
        if lis != None:
            for li in lis:
                obj = {}
                type = li.xpath('.//@data-type')[0]
                print(type)
                time = li.xpath('.//@data-datetime')[0].replace('T', ' ').replace('+08:00', '')
                print(time)

                # if type == 'join_jianshu':
                #     join_jianshu_time = time
                if self.lastest_time == time:
                    return
                # obj['time']=time
                if page == 1 and 'latest_time' not in self.timeline:
                    self.timeline['latest_time'] = time
                if type == 'join_jianshu':
                    self.timeline['join_time'] = time
                    return
                obj['time'] = time
                if type == 'comment_note':
                    obj['comment_text'] = li.xpath('.//p[@class="comment"]/text()')[0]
                    obj['note_id'] = li.xpath('.//a[@class="title"]/@href')[0].split('/')[-1]
                elif type == 'like_note':
                    obj['note_id'] = li.xpath('.//a[@class="title"]/@href')[0].split('/')[-1]
                elif type == 'reward_note':
                    obj['note_id'] = li.xpath('.//a[@class="title"]/@href')[0].split('/')[-1]
                elif type == 'share_note':
                    obj['note_id'] = li.xpath('.//a[@class="title"]/@href')[0].split('/')[-1]
                elif type == 'like_user':
                    obj['slug'] = li.xpath('.//div[@class="follow-detail"]//a[@class="title"]/@href')[0].split('/')[
                        -1]
                elif type == 'like_collection':
                    obj['coll_id'] = li.xpath('.//a[@class="avatar-collection"]/@href')[0].split('/')[-1]
                elif type == 'like_comment':
                    try:
                        obj['comment_text'] = li.xpath('.//p[@class="comment"]/text()')[0]
                    except IndexError:
                        print('Error:list index out of range')
                    obj['slug'] = li.xpath('.//blockquote/div/a/@href')[0].split('/')[-1]
                    obj['note_id'] = li.xpath('.//blockquote/div/span/a/@href')[0].split('/')[-1]
                elif type == 'like_notebook':
                    obj['notebook_id'] = li.xpath('.//a[@class="avatar-collection"]/@href')[0].split('/')[-1]
                elif type == 'reward_user':
                    obj['slug']=li.xpath('.//a[@class="title"]/@href')[0].split('/')[-1]

                else:
                    pass
                lst = self.timeline[type]
                lst.append(obj)

        # pprint(timeline)
        self.get_user_timeline( maxid, page + 1)

    def get_base_info(self):
        url = f'http://www.jianshu.com/u/{self.slug}'
        response = requests.get(url, headers=self.BASE_HEADERS)
        if response.status_code == 404:
            '''经测试，出现404时都是因为用户被封禁或注销，即显示：
            您要找的页面不存在.可能是因为您的链接地址有误、该文章已经被作者删除或转为私密状态。'''
            return None
        else:
            tree = etree.HTML(response.text)

            div_main_top = tree.xpath('//div[@class="main-top"]')[0]
            nickname = div_main_top.xpath('.//div[@class="title"]//a/text()')[0]
            head_pic = div_main_top.xpath('.//a[@class="avatar"]//img/@src')[0]
            div_main_top.xpath('.//div[@class="title"]//i/@class')

            # 检查用户填写的性别信息。1：男  -1：女  0：性别未填写
            if div_main_top.xpath('.//i[@class="iconfont ic-man"]'):
                gender = 1
            elif div_main_top.xpath('.//i[@class="iconfont ic-woman"]'):
                gender = -1
            else:
                gender = 0

            # 判断该用户是否为签约作者。is_contract为1是简书签约作者，为0则是普通用户
            if div_main_top.xpath('.//i[@class="iconfont ic-write"]'):
                is_contract = 1
            else:
                is_contract = 0

            # 取出用户文章及关注量
            info = div_main_top.xpath('.//li//p//text()')

            item = {'nickname': nickname,
                    'slug': self.slug,
                    'head_pic': head_pic,
                    'gender': gender,
                    'is_contract': is_contract,
                    'following_num': int(info[0]),
                    'followers_num': int(info[1]),
                    'articles_num': int(info[2]),
                    'words_num': int(info[3]),
                    'be_liked_num': int(info[4]),
                    'update_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    }
            # 取当前抓取时间，为用户信息更新时间。添加update_time字段
            return item
    def get_lastest_time(self):
        result=self.db['user_timeline'].find_one({'slug':self.slug},{'latest':1})
        if result != None:
            self.lastest_time = self.db['user_timeline'].find_one({'slug': self.slug}, {'latest_time': 1}).get('latest_time')
        else:
            self.lastest_time=None
    def add_user_timeline_to_mongodb(self,all_user_info):
        self.db['user_timeline'].update_one({'slug':self.slug},{'$set':all_user_info},upsert=True)
    # 实现断点续爬
    def append_user_timeline_to_mongodb(self):
        if 'latest_time' in self.timeline:
            self.db['user_timeline'].update_one({'slug': self.slug}, {'$set': {'latest_time': self.timeline['latest_time']}}, upsert=True)
        for type in self.timeline.keys():
            if len(self.timeline[type]) > 0 and type != 'latest_time':
                self.db['user_timeline'].update_one({'slug': self.slug}, {'$push': {type: {'$each': self.timeline[type]}}})
if __name__ == '__main__':
    slug='df56c9f72b32'
    js=JianshuSpider(slug)
    js.get_lastest_time()

    item=js.get_base_info()
    pprint(item)

    js.get_user_timeline(None,1)
    print('采集所有动态结束')
    pprint(js.timeline)

    all_user_info = dict(item,**js.timeline)
    if 'join_time' in js.timeline:
        js.add_user_timeline_to_mongodb(all_user_info)
    else:
        js.append_user_timeline_to_mongodb()



