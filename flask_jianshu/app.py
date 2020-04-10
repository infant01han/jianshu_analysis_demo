# -*- coding: utf-8 -*-
# @Time    : 2020/4/7 0007 16:39
# @Author  : Han lei
# @Email   : hanlei5012@163.com
# @File    : app.py
# @Software: PyCharm
import re
from pprint import pprint



from flask import Flask, render_template, request, redirect, url_for
import sys

from flask_jianshu.jianshu_dynamic_analysis import AnalysisUser
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
            # print(slug)
            # get_user_timeline(slug)
            return redirect(url_for('jianshu_timeline',slug=slug))
        else:
            return render_template('index.html',error_msg='输入的简书主页有问题，请重新输入')
        print(url)
    return render_template('index.html')

def get_user_dynamic_info(slug):
    js = JianshuSpider(slug)
    js.get_lastest_time()
    item = js.get_base_info()
    pprint(item)
    js.get_user_timeline(None,1)
    print('采集所有动态完毕')
    pprint(js.timeline)
    all_user_info = dict(item, **js.timeline)
    if 'join_time' in js.timeline:
        js.add_user_timeline_to_mongodb(all_user_info)
    else:
        js.append_user_timeline_to_mongodb()

@app.route('/timeline')
def jianshu_timeline():
    slug = request.args.get('slug')
    #采集用户全部动态并保存到mongodb
    get_user_dynamic_info(slug)
    au = AnalysisUser(slug)
    #从mongodb中获取动态
    user_base_info = au.get_user_base_info()
    first_info=au.get_first_info()
    tags_data = au.get_tags_data()

    month_data_dic=au.get_month_data()
    day_data_dic=au.get_day_data()
    hour_data_dic=au.get_hour_data()
    week_data_dic=au.get_week_data()
    week_hour_data_dic=au.get_week_hour_data()

    word_cloud_lst=au.get_word_cloud_data()
    return render_template('timeline.html',baseinfo=user_base_info,first_tag_time=first_info,tags_data=tags_data,month_data_dic=month_data_dic,day_data_dic=day_data_dic,hour_data_dic=hour_data_dic,week_data_dic=week_data_dic,week_hour_data_dic=week_hour_data_dic,word_cloud_lst=word_cloud_lst)
if __name__ == '__main__':
    # slug = 'b325abe9131e'
    # slug='df56c9f72b32'
    # js = JianshuSpider(slug)
    # item=js.get_lastest_and_join_time()
    # pprint(item)
    #
    #
    # js.get_user_timeline(None, 1)
    # print('采集所有动态完毕')
    #
    # pprint(js.timeline)
    #
    # all_user_info = dict(item, **js.timeline)
    #
    # if 'join_time' in js.timeline:
    #     js.add_user_timeline_to_mongodb(all_user_info)
    # else:
    #     js.append_user_timeline_to_mongodb()
    app.run()