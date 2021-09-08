# -*- coding:utf-8 -*-
from datetime import date
import json
import requests
import sys
from datetime import datetime

from django.db.models import Avg, Max, Min
from django.core.management.base import BaseCommand, CommandError
from stocks.models import Stock, KHistory

import baostock as bs
import pandas as pd

class Command(BaseCommand):
    help = '更新证券数据'
    
    def handle(self, *args, **options):
        
        #### 四个关注指标 ####
        # close 当日收盘价
        # peTTM 滚动市盈率
        # pbMRQ 市净率
        # 

        #### 登陆系统 ####
        lg = bs.login()
        # 显示登陆返回信息
        print('login respond error_code:'+lg.error_code)
        print('login respond  error_msg:'+lg.error_msg)

        my_stocks = Stock.objects.all()
        
        today = datetime.today()
        end_date = today.strftime('%Y-%m-%d')

        for stock in my_stocks:
            #### 获取沪深A股历史K线数据 ####
            # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
            # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
            # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
            all_h_set = KHistory.objects.filter(stock=stock)
            h_date = all_h_set.order_by('-date').aggregate(Max('date'))
            start_date_from_db = h_date.get('date__max')
            
            start_date = '1990-12-19'
            if start_date_from_db is not None:
                start_date = start_date_from_db.strftime('%Y-%m-%d')
            
            print(stock.code, stock.code_name, start_date, end_date)
            
            if start_date != end_date:
                rs = bs.query_history_k_data_plus(stock.code,
                    "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,psTTM,pcfNcfTTM,pbMRQ,isST",
                    start_date=start_date, end_date=end_date,
                    frequency="d", adjustflag="3")
                print('query_history_k_data_plus respond error_code:'+rs.error_code)
                print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)

                #### 打印结果集 ####
                while (rs.error_code == '0') & rs.next():
                    # 获取一条记录，将记录合并在一起
                    x = rs.get_row_data()
                    print(x)
                    try:
                        k = KHistory()
                        k.stock = stock
                        k.date = None if not x[0] else date(*map(int, x[0].split('-')))
                        k.open_price = float(x[2])
                        k.high_price = float(x[3])
                        k.low_price = float(x[4])
                        k.close_price = float(x[5])
                        k.preclose_price = float(x[6])
                        k.volume = float(x[7])
                        k.amount = float(x[8])
                        k.adjust_flag = int(x[9])
                        k.turn = float(x[10])
                        k.trades_tatus = int(x[11])
                        k.pctChg = float(x[12])
                        k.peTTM = float(x[13] if x[13] else 0)
                        k.psTTM = float(x[14] if x[14] else 0)
                        k.pcfNcfTTM = float(x[15] if x[15] else 0)
                        k.pbMRQ = float(x[16] if x[16] else 0)
                        k.is_st = int(x[17] if x[17] else 0)
                        k.save()
                    except Exception as e:
                        print("%s %s cannot be saved. %s" % (x[1], x[0], sys.exc_info()[1]))
            
            
        #### 登出系统 ####
        bs.logout()
