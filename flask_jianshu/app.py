# -*- coding: utf-8 -*-
# @Time    : 2020/4/7 0007 16:39
# @Author  : Han lei
# @Email   : hanlei5012@163.com
# @File    : app.py
# @Software: PyCharm
import re
from pprint import pprint



from flask import Flask, render_template, request
import sys

from flask_jianshu.jianshu_dynamic_spider import JianshuSpider

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



if __name__ == '__main__':
    # slug = 'b325abe9131e'
    slug='df56c9f72b32'
    js = JianshuSpider(slug)
    item=js.get_lastest_and_join_time()
    pprint(item)


    js.get_user_timeline(None, 1)
    print('采集所有动态完毕')

    pprint(js.timeline)

    all_user_info = dict(item, **js.timeline)

    if 'join_time' in js.timeline:
        js.add_user_timeline_to_mongodb(all_user_info)
    else:
        js.append_user_timeline_to_mongodb()