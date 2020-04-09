# -*- coding: utf-8 -*-
# @Time    : 2020/4/9 0009 11:16
# @Author  : Han lei
# @Email   : hanlei5012@163.com
# @File    : jianshu_dynamic_analysis.py
# @Software: PyCharm

import pymongo


class AnalysisUser:
    def __init__(self,slug):
        self.client = pymongo.MongoClient(host='localhost')
        self.db = self.client['JianShu2']
        self.slug = slug
        self.user_data = self.db['user_timeline'].find_one({'slug':self.slug})

    def get_user_base_info(self):
        baseinfo = {'head_pic': self.user_data['head_pic'],
                    'nickname': self.user_data['nickname'],
                    'update_time': self.user_data['update_time'],
                    'like_users_num': self.user_data['following_num'],
                    'followers_num': self.user_data['followers_num'],
                    'share_notes_num': self.user_data['articles_num'],
                    'words_num': self.user_data['words_num'],
                    'be_liked_num': self.user_data['be_liked_num'],
                    'like_notes_num': len(self.user_data['like_note']),
                    'like_colls_num': len(self.user_data['like_collection']),
                    'like_nbs_num': len(self.user_data['like_notebook']),
                    'comment_notes_num': len(self.user_data['comment_note']),
                    'like_comments_num': len(self.user_data['like_comment']),
                    'reward_notes_num': len(self.user_data['reward_note'])
                    }
        # print(baseinfo)
        return baseinfo