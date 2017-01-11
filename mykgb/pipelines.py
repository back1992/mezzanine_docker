# -*- coding: utf-8 -*-

from django.db.models import F
from django.db.models import Q
from django.db.models import Max
from mykgb.sm import sm
# from scrapy.mail import MailSender

import re
from myapp.models import Codeset, Price, Position

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class MykgbPipeline(object):
    def __init__(self):
        # self.receiver = "13261871395@163.com"
        # self.msg_cc = ""
        self.action_msg = ''
        self.title = 'self.title'

    def process_item(self, item, spider):
        self.title = item['title']

        direction = item['macd'] + item['rsi'] + item['kdj'] + item['cci']
        print('direction', direction)
        # print(item)
        if direction < -10:
            self.action_msg += u'<h3 STYLE="color:green;">做空 ' + item['code'] + '</h3>'
            for index in ['macd', 'kdj', 'rsi', 'cci']:
                if item[index] < 0:
                    self.action_msg += u'<p style="color:green">' + index + ':' + str(item[index]) + '</p>'
                elif item[index] > 0:
                    self.action_msg += u'<p style="color:red">' + index + ':' + str(item[index]) + '</p>'
        elif direction > 10:
            self.action_msg += u'<h3 STYLE="color:red;">做多 ' + item['code'] + '</h3>'
            for index in ['macd', 'kdj', 'rsi', 'cci']:
                if item[index] < 0:
                    self.action_msg += u'<p style="color:green">' + index + ':' + str(item[index]) + '</p>'
                elif item[index] > 0:
                    self.action_msg += u'<p style="color:red">' + index + ':' + str(item[index]) + '</p>'
    def close_spider(self, spider):
        if self.action_msg:
            # sm(self.title, self.action_msg, self.receiver, self.msg_cc)
            sm(self.title, self.action_msg)



# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html



class DestinyPipeline(object):
    def __init__(self):
        # self.receiver = "13261871395@163.com"
        # self.msg_cc = ""
        self.action_msg = ''
        self.title = 'self.title'

    def process_item(self, item, spider):
        self.title = item['title']

        direction = item['macd'] + item['rsi'] + item['kdj'] + item['cci']
        print('direction', direction)
        # print(item)
        if direction < -10:
            self.action_msg += u'<h3 STYLE="color:green;">做空 ' + item['code'] + '</h3>'
            for index in ['macd', 'kdj', 'rsi', 'cci']:
                if item[index] < 0:
                    self.action_msg += u'<p style="color:green">' + index + ':' + str(item[index]) + '</p>'
                elif item[index] > 0:
                    self.action_msg += u'<p style="color:red">' + index + ':' + str(item[index]) + '</p>'
        elif direction > 10:
            self.action_msg += u'<h3 STYLE="color:red;">做多 ' + item['code'] + '</h3>'
            for index in ['macd', 'kdj', 'rsi', 'cci']:
                if item[index] < 0:
                    self.action_msg += u'<p style="color:green">' + index + ':' + str(item[index]) + '</p>'
                elif item[index] > 0:
                    self.action_msg += u'<p style="color:red">' + index + ':' + str(item[index]) + '</p>'

    def close_spider(self, spider):
        print(self.action_msg)
        if self.action_msg:
            print(self.action_msg)
            # sm(self.title, self.action_msg, self.receiver, self.msg_cc)
            sm(self.title, self.action_msg)


class PositionPipeline(object):
    def __init__(self):
        self.name_list = [u"永安期货", u"混沌天成"]
        self.receiver = "13261871395@163.com"
        self.msg_cc = ""
        try:
            self.last_date = Position.objects.all().aggregate(Max('date'))['date__max']
        except:
            raise ValueError('no position data in db')

    def process_item(self, item, spider):
        pass

    def close_spider(self, spider):
        # self.last_date = Position.objects.all().aggregate(Max('date'))['date__max']
        for name in self.name_list:
            self.position_flag(name, self.last_date, self.msg_cc)

    def position_flag(self, name, date, cc=''):
        signal = ''
        positions = Position.objects.filter(name=name, date=date).filter(
            ~Q(buyposition=0) & ~Q(sellposition=0)).annotate(
            hold_interest=F('buyposition') - F('sellposition'),
            hold_var=F('buyvar') - F('sellvar'),
            strength_interest=(F('buyposition') - F('sellposition')) * 100 / (F('buyposition') + F('sellposition')),
            # strength_var=F('hold_var') * 100 / (F('buyposition') + F('sellposition'))
            strength_var=(F('buyvar') - F('sellvar')) * 100 / (F('buyposition') + F('sellposition'))
        ).order_by(
            'strength_interest')
        for p in positions:

            signal += '<h3>' + p.code.codezh + ' ' + p.code.maincontract + '</h3>\n'
            signal += u'<p>多单仓位: ' + str(p.buyposition) + u'  多头排名: ' + str(p.buyno) + u'   仓位变化: ' + str(
                p.buyvar) + '</p>'
            signal += u'<p>空单仓位: ' + str(p.sellposition) + u'  空头排名: ' + str(p.sellno) + u'   仓位变化: ' + str(
                p.sellvar) + '</p>'
            if p.hold_interest > 0:
                signal += u'<p style="color:red;">净多仓位: ' + str(p.hold_interest) + '</p>'
                signal += u'<p style="color:red;">持仓强度 多: ' + str(p.strength_interest) + '</p>'
            else:
                signal += u'<p style="color:green;">净空仓位: ' + str(p.hold_interest) + '</p>'
                signal += u'<p style="color:green;">持仓强度 空: ' + str(p.strength_interest) + '</p>'
            if p.hold_var > 0:
                signal += u'<p style="color:red;">交易方向 多: ' + str(p.hold_var) + '</p>'
                signal += u'<p style="color:red;">交易强度 多: ' + str(p.strength_var) + '</p>'
            else:
                signal += u'<p style="color:green;">交易方向 空: ' + str(p.hold_var) + '</p>'
                signal += u'<p style="color:green;">交易强度 空: ' + str(p.strength_var) + '</p>'
        if signal:
            sm(name + u"主力合约持仓指数 " + date.strftime('%Y-%m-%d'), signal, self.receiver, cc)



