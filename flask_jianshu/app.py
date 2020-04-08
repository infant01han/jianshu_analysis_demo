# -*- coding: utf-8 -*-
# @Time    : 2020/4/7 0007 16:39
# @Author  : Han lei
# @Email   : hanlei5012@163.com
# @File    : app.py
# @Software: PyCharm
import re
import time
from pprint import pprint

from lxml import etree

import requests
from fake_useragent import UserAgent
from flask import Flask, render_template, request
import sys
sys.setrecursionlimit(6000) #设置这个可以突破递归限制

app=Flask(__name__)
@app.route('/',methods=['GET','POST'])
def home():
    if request.method == 'POST':
        url = request.form['url']
        match_result=re.match(r'(https://)?(www.jianshu.com/u/)?(\w{12}|\w{6})$',url)
        if match_result:
            slug=match_result.groups()[-1]
            print(slug)
            # get_user_timeline(slug)
        else:
            return render_template('index.html',error_msg='输入的简书主页有问题，请重新输入')
        print(url)
    return render_template('index.html')

BASE_HEADERS = {
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
timeline = {
    'comment_note': [],
    'like_note': [],
    'reward_note': [],
    'share_note': [],
    'like_user': [],  # 用户id
    'like_collection': [],  # 文集id
    'like_comment': [],
    'like_notebook': [],  # 专题id
}
join_jianshu_time = ''
def get_user_timeline(slug,maxid,page):
    global join_jianshu_time
    print(f'正在抓取第{page}页')
    AJAX_HEADERS = {"Referer": "http//:www.jianshu.com/u/{slug}".format(slug=slug),
                    "X-PJAX": "true"}
    headers = dict(BASE_HEADERS, **AJAX_HEADERS)
    if maxid==None:
        url=f'https://www.jianshu.com/users/{slug}/timeline'
    else:
        url=f'https://www.jianshu.com/users/{slug}/timeline?max_id={maxid}&page={page}'
    rsp = requests.get(url,headers=headers)
    # print(rsp.text)
    tree = etree.HTML(rsp.text)#将回应变成xml的树，可以用xpath解析
    lis = tree.xpath('.//li')
    last_li_id=lis[-1].xpath('@id')[0].replace('feed-','')
    print(last_li_id)
    maxid = int(last_li_id)-1
    if lis != None:
        for li in lis:
            obj={}
            type = li.xpath('.//@data-type')[0]
            print(type)
            time = li.xpath('.//@data-datetime')[0].replace('T',' ').replace('+08:00','')
            print(time)

            if type == 'join_jianshu':
                join_jianshu_time = time
                return
            obj['time']=time
            if type=='comment_note':
                obj['comment_text']=li.xpath('.//p[@class="comment"]/text()')[0]
                print(obj['comment_text'])
                obj['note_id']=li.xpath('.//a[@class="title"]/@href')[0].split('/')[-1]
                print(f"note_id:{obj['note_id']}")
            elif type==['like_note']:
                pass
            else:
                pass
            lst=timeline[type]
            lst.append(obj)

    # pprint(timeline)
    get_user_timeline(slug,maxid,page+1)
def get_base_info(slug):
    url = f'http://www.jianshu.com/u/{slug}'
    response = requests.get(url, headers=BASE_HEADERS)
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
                'slug': slug,
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


if __name__ == '__main__':
    slug = 'b325abe9131e'
    get_user_timeline(slug,None,1)
    print('采集所有动态完毕')
    pprint(timeline)
    # print(f'加入简书时间：{join_jianshu_time}')
    # item = get_base_info(slug)
    # pprint(item)
    # app.run()