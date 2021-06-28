# -*- coding:utf-8 -*-
from datetime import date
import json
import requests

from django.core.management.base import BaseCommand, CommandError
from stocks.models import Stock, KHistory

import baostock as bs
import pandas as pd

class Command(BaseCommand):
    help = '导入证券数据'
    
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

        for stock in my_stocks:
            #### 获取沪深A股历史K线数据 ####
            # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
            # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
            # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
            rs = bs.query_history_k_data_plus(stock.code,
                "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,psTTM,pcfNcfTTM,pbMRQ,isST",
                start_date='1990-12-19', end_date='2021-06-14',
                frequency="d", adjustflag="3")
            print('query_history_k_data_plus respond error_code:'+rs.error_code)
            print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)

            #### 打印结果集 ####
            while (rs.error_code == '0') & rs.next():
                # 获取一条记录，将记录合并在一起
                x = rs.get_row_data()
                #print(x)
                try:
                    k = KHistory()
                    k.stock = stock
                    k.date = None if not x[0] else date(*map(int, x[0].split('-')))
                    k.open_price = str(x[2])
                    k.high_price = str(x[3])
                    k.low_price = str(x[4])
                    k.close_price = str(x[5])
                    k.preclose_price = str(x[6])
                    k.volume = str(x[7])
                    k.amount = str(x[8])
                    k.adjust_flag = int(x[9])
                    k.turn = str(x[10])
                    k.trades_tatus = int(x[11])
                    k.pctChg = str(x[12])
                    k.peTTM = str(x[13])
                    k.psTTM = str(x[14])
                    k.pcfNcfTTM = str(x[15])
                    k.pbMRQ = str(x[16])
                    k.is_st = int(x[17] if x[17] else 0)
                    k.save()
                except Exception as e:
                    print("%s %s cannot be saved. %s" % (k[1], k[0], sys.exc_info()))
                    
        #### 登出系统 ####
        bs.logout()
