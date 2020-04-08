# -*- coding: utf-8 -*-
# @Time    : 2020/4/7 0007 14:18
# @Author  : Han lei
# @Email   : hanlei5012@163.com
# @File    : JianshuSpider.py
# @Software: PyCharm
import scrapy
from fake_useragent import UserAgent
from scrapy import Request

from jianshu_spider.items import JianshuSpiderItem


class JianshuSpider(scrapy.Spider):
    name='jian_spider'

    base_headers = {'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
                    'Host': 'www.jianshu.com',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'text/html, */*; q=0.01',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
                    'Connection': 'keep-alive',
                    'Referer': 'http://www.jianshu.com'}
    # 只加载列表模块,这里是为了随机变化User-Agent欺骗服务器
    #为什么用这个请求头，因为简书的推荐用户页面用的是pjax请求
    ajax_headers = dict(base_headers, **{"X-PJAX": "true", 'User-Agent': UserAgent().random})

    def start_requests(self):
        url='https://www.jianshu.com/recommendations/users?page=1&per_page=200'
        yield Request(url,headers=self.ajax_headers)

    def parse(self, response):
        print(response.text)
        userlist = response.xpath('.//div[@class="wrap"]//a/@href').extract()
        print(userlist)
        for user_href in userlist:
            user_slug=user_href.replace('/users/','')
            yield Request(f'https://www.jianshu.com/u/{user_slug}'
                          ,headers=self.base_headers
                          ,callback=self.parse_user
                          ,meta={'user_slug':user_slug})
            yield Request(f'https://www.jianshu.com/users/{user_slug}/followers？page=1',headers=self.ajax_headers,callback=self.parse_user_followers,
                          meta={'slug':user_slug,'page':1})

    def parse_user(self,response):
        base_info_item = JianshuSpiderItem()
        slug = response.meta['user_slug']
        div_main_top = response.xpath('//div[@class="main-top"]')
        nickname = div_main_top.xpath('.//div[@class="title"]//a/text()').extract_first()
        head_pic = div_main_top.xpath('.//a[@class="avatar"]//img/@src').extract_first()
        gender_tmp = div_main_top.xpath('.//div[@class="title"]//i/@class').extract()
        if gender_tmp:
            gender = gender_tmp[0].split('-')[-1]
        else:
            gender = 'No'
        is_contract_tmp = div_main_top.xpath('.//div[@class="title"]//span[@class="author-tag"]').extract()
        if is_contract_tmp:
            is_contract = '签约作者'
        else:
            is_contract = 'No'
        info = div_main_top.xpath('.//li//p//text()').extract()

        base_info_item['nickname'] = nickname
        base_info_item['slug'] = slug
        base_info_item['head_pic'] = head_pic
        base_info_item['gender'] = gender
        base_info_item['is_contract'] = is_contract
        base_info_item['following_num'] = int(info[0])
        base_info_item['followers_num'] = int(info[1])
        base_info_item['articles_num'] = int(info[2])
        base_info_item['words_num'] = int(info[3])
        base_info_item['be_liked_num'] = int(info[4])
        yield base_info_item
    def parse_user_followers(self,response):
        slug=response.meta['user_slug']
        page=response.meta['page']+1
        url = f'https://www.jianshu.com/users/{slug}/followers？page={page}'
        yield Request(url,headers=self.ajax_headers,callback=self.parse_user_followers,meta={'user_slug':slug,'page':page})
        #解析出粉丝列表userlist
        # for user in userlist:
            # 解析出该粉丝信息保存到JianshuSpiderItem,并yield item
            # yield request(该粉丝的用户详情）
        pass