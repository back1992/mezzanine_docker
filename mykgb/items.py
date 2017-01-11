# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field
# from scrapy_djangoitem import DjangoItem


class MykgbItem(scrapy.Item):
    title = Field()
    code = Field()
    macd = Field()
    kdj = Field()
    cci = Field()
    rsi = Field()
