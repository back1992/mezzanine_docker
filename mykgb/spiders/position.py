# -*- coding: utf-8 -*-
import datetime
import scrapy
from mykgb.items import *
from myapp.models import Codeset, Price, Position


class PositionSpider(scrapy.Spider):
    name = "position"
    allowed_domains = ["hexun.com", 'baidu.com']
    start_urls = ['http://www.baidu.com/']

    custom_settings = {
        'ITEM_PIPELINES': {
            'mykgb.pipelines.PositionPipeline': 100,
        },
    }

    def parse(self, response):
        # Position.objects.all().delete()
        date_price = set(Price.objects.order_by('-date').values_list('date', flat=True).distinct()[:30])
        date_position = set(Position.objects.values_list('date', flat=True).distinct())
        date_set = date_price - date_position
        today = datetime.datetime.today()
        if not today in date_set:
            date_set.add(today)
        qs = Codeset.objects.filter(actived=True)
        for p in qs:
            for date in date_set:
                date = date.strftime('%Y-%m-%d')
                url = 'http://data.futures.hexun.com/cccj.aspx?sBreed=' + p.sbreed + '&sContract=' + p.maincontract + '&sDate=' + date + '&sRank=2000'
                yield scrapy.Request(url, meta={'code': p.codeen, 'date': date, 'url': url},
                                     callback=self.parsePage)

    def parsePage(self, response):
        tables = response.xpath('//table[@class="dou_table"]')
        types = {'0': 'trade', '1': 'buy', '2': 'sell'}
        for typeindex, typevalue in types.items():
            for tr in tables[int(typeindex)].xpath('./tr')[1:]:
                tds = tr.xpath('./td')
                code = Codeset.objects.get(codeen=response.meta['code'])
                date = response.meta['date']
                name = tds[1].xpath('./div/a/text()').extract_first()
                p, created = Position.objects.update_or_create(code=code, name=name, date=date)
                setattr(p, typevalue + 'no', tds[0].xpath('./text()').extract_first())
                setattr(p, typevalue + 'position', tds[2].xpath('./text()').extract_first())
                setattr(p, typevalue + 'var', tds[3].xpath('./text()').extract_first())
                p.save()
        date = response.meta['date']
        code = response.meta['code']

        page_index = response.xpath('//*[@id="mainbox"]/div[3]/div[15]/strong/text()').extract_first()
        if (page_index):
            leadurl = response.meta['url']
            totalpages = page_index.split('/')[1]
            for page in range(1, int(totalpages) + 1):
                url = leadurl + '&page=' + str(page)
                yield scrapy.Request(url, meta={'code': code, 'date': date, 'url': response.meta['url']},
                                     callback=self.parsePage)
