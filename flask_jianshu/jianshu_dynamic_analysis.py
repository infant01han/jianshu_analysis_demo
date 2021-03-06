# -*- coding: utf-8 -*-
# @Time    : 2020/4/9 0009 11:16
# @Author  : Han lei
# @Email   : hanlei5012@163.com
# @File    : jianshu_dynamic_analysis.py
# @Software: PyCharm
from collections import Counter
from datetime import datetime

import jieba
import pymongo
import pandas as pd


class AnalysisUser:
    def __init__(self,slug):
        self.client = pymongo.MongoClient(host='localhost')
        self.db = self.client['JianShu2']
        self.slug = slug
        self.user_data = self.db['user_timeline'].find_one({'slug':self.slug})
        self.zh_parent_tags=['发表评论', '喜欢文章', '赞赏文章', '发表文章', '关注用户', '关注专题', '点赞评论', '关注文集']
        self.en_parent_tags=['comment_note', 'like_note', 'reward_note', 'share_note', 'like_user', 'like_collection', 'like_comment', 'like_notebook']
        df_lst=[]
        for tag in self.en_parent_tags:
            df=pd.DataFrame(self.user_data[tag])
            df_lst.append(df)
        self.df=pd.concat(df_lst)

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

    def extract_first_tag_time(self,data_list):
        if len(data_list)>0:
            sorted_lst=sorted(data_list,key=lambda obj:obj['time'])
            first_element=sorted_lst[0]
            return first_element
        else:
            return None
    def get_first_info(self):
        first_tag_time = {
            'join_time': self.user_data['join_time'],
            'first_like_user': self.extract_first_tag_time(self.user_data['like_user']),
            'first_share_note': self.extract_first_tag_time(self.user_data['share_note']),
            'first_like_note': self.extract_first_tag_time(self.user_data['like_note']),
            'first_like_coll': self.extract_first_tag_time(self.user_data['like_collection']),
            'first_like_nb': self.extract_first_tag_time(self.user_data['like_notebook']),
            'first_comment': self.extract_first_tag_time(self.user_data['comment_note']),
            'first_like_comment': self.extract_first_tag_time(self.user_data['like_comment']),
            'first_reward_note': self.extract_first_tag_time(self.user_data['reward_note']),
        }
        return first_tag_time

    # [
    #     {value: 335, name: '关注用户'},
    #     {value: 310, name: '邮件营销'},
    #     {value: 234, name: '联盟广告'},
    #     {value: 135, name: '视频广告'},
    #     {value: 1548, name: '搜索引擎'}
    # ]

    def get_tags_data(self):
        tags_zh_names_lst = [{'name':zh_name} for zh_name in self.zh_parent_tags]
        tags_values = [{'value':len(self.user_data[tag])} for tag in self.en_parent_tags]
        tags_data = [dict(tags_zh_names_lst[i], **tags_values[i]) for i in range(len(tags_values))]
        return tags_data

    def get_month_data_pd(self):
        dt_index=pd.to_datetime(list(self.df.time))
        ts=pd.Series([1]*len(dt_index),index=dt_index)
        tsday = ts.resample("1M").sum()

        lstMonth=[x.strftime('%Y-%m') for x in tsday[tsday>0].index]
        lst_freq=list(tsday[tsday>0].values)
        dic={}
        dic['month']=lstMonth
        dic['frequency']=list(map(int,lst_freq))
        return dic

    def get_day_data_pd(self):
        dt_index = pd.to_datetime(list(self.df.time))
        ts = pd.Series([1] * len(dt_index), index=dt_index)
        tsday = ts.resample("1D").sum()

        lstDay = [x.strftime('%Y-%m-%d') for x in tsday[tsday > 0].index]
        lst_freq = list(tsday[tsday > 0].values)
        dic = {}
        dic['day'] = lstDay
        dic['frequency'] = list(map(int,lst_freq))
        return dic

    def get_hour_data_pd(self):
        dti=pd.to_datetime(self.df.time).to_frame()  # 转换成dataframe类型
        dayofweek_group=dti.groupby(dti['time'].map(lambda x:x.hour)).count()
        lst_freq=[int(item) for item in dayofweek_group.values]
        lst_dayofweek=[str(item).rjust(2,'0')+':00' for item in dayofweek_group.index]

        dic = {}
        dic['hour'] = lst_dayofweek
        dic['frequency'] = lst_freq
        return dic



    def get_week_data_pd(self):
        dti = pd.to_datetime(self.df.time).to_frame()  # 转换成dataframe类型
        dayofweek_group = dti.groupby(dti['time'].map(lambda x: x.dayofweek)).count()
        week_day_dict = {0: '周一', 1: '周二', 2: '周三', 3: '周四',
                         4: '周五', 5: '周六', 6: '周日', }
        lst_freq = [int(item) for item in dayofweek_group.values]
        lst_dayofweek = [week_day_dict[item] for item in dayofweek_group.index]

        dic = {}
        dic['week'] = lst_dayofweek
        dic['frequency'] = lst_freq
        return dic

    def get_week_hour_data_pd(self):
        dti=pd.to_datetime(self.df.time).to_frame()
        gg=dti.groupby([dti['time'].map(lambda x:x.dayofweek).rename('dayofweek'),dti['time'].map(lambda x:x.hour).rename('hour')])
        gg_count=gg.count()

        lst_week_hour_data=[]
        max_freq=0
        for name,grp in gg:
            print(name)#(周几,几点)
            freq=gg_count.loc[name].values[0]#频率，次数
            if max_freq<freq:
                max_freq=freq
            tmp_lst=[int(name[0]),int(name[1]),int(freq)]
            lst_week_hour_data.append(tmp_lst)

        dic={}
        dic['week_hour']=lst_week_hour_data
        dic['maxFreq']=max_freq
        return dic

    def get_month_data(self):
        all_time_lst=[]
        for type in self.en_parent_tags:
            type_lst=[obj['time'][:7] for obj in self.user_data[type]]
            all_time_lst.extend(type_lst)

        counter = Counter(all_time_lst)
        sorted_lst = sorted(counter.items(),key=lambda x:x[0])
        month_lst=[item[0] for item in sorted_lst]
        frequency_lst = [item[1] for item in sorted_lst]

        dic={}
        dic['month']=month_lst
        dic['frequency']=frequency_lst
        return dic

    def get_day_data(self):
        all_time_lst=[]
        for type in self.en_parent_tags:
            type_lst=[obj['time'][:10] for obj in self.user_data[type]]
            all_time_lst.extend(type_lst)

        counter = Counter(all_time_lst)
        sorted_lst = sorted(counter.items(),key=lambda x:x[0])
        month_lst=[item[0] for item in sorted_lst]
        frequency_lst = [item[1] for item in sorted_lst]

        dic={}
        dic['day']=month_lst
        dic['frequency']=frequency_lst
        return dic

    def get_hour_data(self):
        all_time_lst=[]
        for type in self.en_parent_tags:
            type_lst=[obj['time'][11:13] for obj in self.user_data[type]]
            all_time_lst.extend(type_lst)

        counter = Counter(all_time_lst)
        sorted_lst = sorted(counter.items(),key=lambda x:x[0])
        month_lst=[item[0] for item in sorted_lst]
        frequency_lst = [item[1] for item in sorted_lst]

        dic={}
        dic['hour']=month_lst
        dic['frequency']=frequency_lst
        return dic
    def get_week_data(self):
        week_dic={0:'星期一',1:'星期二',2:'星期三',3:'星期四',4:'星期五',5:'星期六',6:'星期日'}
        all_time_lst=[]
        for type in self.en_parent_tags:
            type_lst=[obj['time'][:10] for obj in self.user_data[type]]
            all_time_lst.extend(type_lst)
        all_week_lst=[datetime.strptime(item,'%Y-%m-%d').weekday() for item in all_time_lst]

        counter = Counter(all_week_lst)
        sorted_lst = sorted(counter.items(),key=lambda x:x[0])
        month_lst=[week_dic[item[0]] for item in sorted_lst]
        frequency_lst = [item[1] for item in sorted_lst]

        dic={}
        dic['week']=month_lst
        dic['frequency']=frequency_lst
        print(dic)
        return dic
    def get_week_hour_data(self):
        like_note_lst=[obj['time'][:13] for obj in self.user_data['like_note']]
        all_like_note_lst=[(str(datetime.strptime(item[:10],'%Y-%m-%d').weekday())+item[11:13]) for item in like_note_lst]

        counter = Counter(all_like_note_lst)
        maxFreq = counter.most_common(1)[0][1]
        sorted_lst = sorted(counter.items(),key=lambda x:x[0])

        lst=[]
        for tp in sorted_lst:
            lstTmp=[int(tp[0][0]),int(tp[0][1:]),tp[1]]
            lst.append(lstTmp)
        print(lst)

        dic={}
        dic['week_hour']=lst
        dic['maxFreq']=maxFreq
        return dic
    def get_word_cloud_data(self):
        word_cloud_data=[obj['comment_text'] for obj in self.user_data['comment_note']]
        count = len(self.user_data['comment_note'])
        word_cloud_str=''.join(word_cloud_data)
        word_cloud_lst=jieba.cut(word_cloud_str)
        wordlstnew=[w for w in word_cloud_lst if len(w)>=2]
        # [{
        #     name: " 没有",
        #     value: 30,
        # },
        counter = Counter(wordlstnew)
        sorted_lst = sorted(counter.items(),key=lambda x:x[1])
        data_lst=[{'name':item[0],'value':item[1]} for item in sorted_lst]

        dic_return = {}
        dic_return['count']=count
        dic_return['word_cloud']=data_lst

        return dic_return