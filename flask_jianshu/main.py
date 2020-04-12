# -*- coding: utf-8 -*-
# @Time    : 2020/4/11 0011 22:18
# @Author  : Han lei
# @Email   : hanlei5012@163.com
# @File    : main.py
# @Software: PyCharm
import pymongo

from flask_jianshu.app import get_user_dynamic_info


if __name__ == '__main__':
    #连接数据库，遍历取出用户信息slug
    client=pymongo.MongoClient(host='localhost',)
    db=client['JianShu2']
    user_data_lst=db['user'].find()
    for user_data in user_data_lst:
        user_slug=user_data['slug']
        get_user_dynamic_info(user_slug)