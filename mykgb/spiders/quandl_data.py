# -*- coding: utf-8 -*-
import scrapy
import numpy
import quandl
from mykgb import indicator
from myapp.models import Quandlset
from mykgb.items import MykgbItem

quandl.ApiConfig.api_key = "taJyZN8QXqj2Dj8SNr6Z"
quandl.ApiConfig.api_version = '2015-04-09'


class QuandlDataSpider(scrapy.Spider):
    name = "quandl_data"
    allowed_domains = ["www.baidu.com"]
    start_urls = ['http://www.baidu.com/']

    custom_settings = {
        'ITEM_PIPELINES': {
            # 'mykgb.pipelines.DestinyPipeline': 100
            'mykgb.pipelines.MykgbPipeline': 100
        },
        'DEFAULT_REQUEST_HEADERS': {
            'Referer': 'http://www.baidu.com'
        }
    }

    def parse(self, response):
        # Quandlset.objects.update(actived=True)
        qs = Quandlset.objects.filter(actived=True)
        for p in qs:
            symbol = p.quandlcode + "1"
            if p and p.namezh:
                code_str = p.namezh + ' ' + p.exchange + ' ' + p.name
            else:
                code_str = p.exchange + ' ' + p.name

            # p.actived = True
            # p.save()
            try:
                df = quandl.get(symbol)[-100:]
            except:
                print("error", symbol)
                continue
            if 'Last' in df.columns:
                df = df.rename(
                    # columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Volume': 'volume', 'Last': 'close'})
                    columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Last': 'close'})
            elif 'Close' in df.columns:
                df = df.rename(
                    # columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Volume': 'volume', 'Close': 'close'})
                    columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})
            elif 'Settle' in df.columns:
                df = df.rename(
                    # columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Volume': 'volume', 'Settle': 'close'})
                    columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Settle': 'close'})
            else:
                p.actived = False
                p.save()
                continue
            # df[df['volume'] == 0] = numpy.nan
            df = df.dropna()

            if not df.empty and df.shape[0] > 50:
                item = MykgbItem()
                item['title'] = 'sleepless money'
                item['code'] = code_str
                macd = indicator.get_macd(df)
                kdj = indicator.get_kdj(df)
                rsi = indicator.get_rsi(df)
                cci = indicator.get_cci(df)
                item['macd'] = sum(macd.values())
                item['kdj'] = sum(kdj.values())
                item['rsi'] = sum(rsi.values())
                item['cci'] = sum(cci.values())
                yield item
