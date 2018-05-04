# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name=scrapy.Field()
    price=scrapy.Field()
    rating=scrapy.Field()#评价等级
    upc=scrapy.Field()#UCP编码
    stock=scrapy.Field()#库存
    num=scrapy.Field()#评价数量 