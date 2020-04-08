# -*- coding: utf-8 -*-
# @Time    : 2020/4/7 0007 16:39
# @Author  : Han lei
# @Email   : hanlei5012@163.com
# @File    : app.py
# @Software: PyCharm
import re
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
    'like_user': [],
    'like_coll': [],
    'like_comment': [],
    'like_notebook': [],
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
            type = li.xpath('.//@data-type')[0]
            print(type)
            time = li.xpath('.//@data-datetime')[0].replace('T',' ').replace('+08:00','')
            print(time)

            if type == 'join_jianshu':
                join_jianshu_time = time
                return

            lst=timeline[type]
            lst.append(time)

    # pprint(timeline)
    get_user_timeline(slug,maxid,page+1)

if __name__ == '__main__':
    slug = 'df56c9f72b32'
    get_user_timeline(slug,None,1)
    print('采集所有动态完毕')
    pprint(timeline)
    print(f'加入简书时间：{join_jianshu_time}')
    # app.run()