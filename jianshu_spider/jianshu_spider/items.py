# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JianshuSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    nickname = scrapy.Field()
    slug = scrapy.Field()  #用户id
    head_pic = scrapy.Field()
    gender = scrapy.Field()
    is_contract = scrapy.Field()#签约用户
    following_num = scrapy.Field()
    followers_num = scrapy.Field()
    articles_num = scrapy.Field()
    words_num = scrapy.Field()
    be_liked_num = scrapy.Field()
