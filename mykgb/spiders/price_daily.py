# -*- coding: utf-8 -*-
import scrapy
import datetime

import pandas as pd
from django.db.models import Max
from myapp.models import *
from mykgb.items import *
from datetime import datetime


class PriceDailySpider(scrapy.Spider):
    name = "price_daily"
    allowed_domains = ["*"]
    qs = Codeset.objects.filter(actived=True)
    start_urls = (
        'http://stock2.finance.sina.com.cn/futures/api/json.php/%s?symbol=%s' % (
            'IndexService.getInnerFuturesDailyKLine',
            code.maincontract)
        for code in qs)

    def parse(self, response):
        codeen = response.url.split('=')[-1][:-4]
        code = Codeset.objects.get(codeen=codeen)
        df = pd.read_json(response.url)
        df = pd.DataFrame({'date': df[0], 'open': df[1], 'high': df[2], 'low': df[3], 'close': df[4], 'volume': df[5]})
        # df.set_index('date', inplace=True)
        # df['date'] = datetime.strptime(df['date'], '%Y-%m-%s')
        df.set_index('date')
        last_date = Price.objects.filter(code=code).aggregate(Max('date'))['date__max']
        print(last_date)
        if last_date:
            df = df[df['date'] > last_date.strftime('%Y-%m-%d')]
            # print(df[:5])
        else:
            print(code, 'price in empty')

        df_records = df.to_dict('records')
        # print(df_records[:5])
        model_instances = [Price(
            code=code,
            # date=record['date'],
            date=datetime.strptime(record['date'], '%Y-%m-%d'),
            open=record['open'],
            high=record['high'],
            low=record['low'],
            close=record['close'],
            volume=record['volume'],
        ) for record in df_records]

        Price.objects.bulk_create(model_instances)
