# -*- coding:utf-8 -*-
from datetime import date, timedelta
import json
import requests

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Avg, Max, Min
from stocks.models import Stock, KHistory

import baostock as bs
import pandas as pd

from math import floor

class Command(BaseCommand):
    help = '回溯测试'
    
    def handle(self, *args, **options):
        
        #### 四个关注指标 ####
        # close 当日收盘价
        # peTTM 滚动市盈率

        my_stocks = Stock.objects.all()

        for s in my_stocks:
            
            # 总资本
            money = 100000
            # 持有股票数量
            s_count = 0
            # 开启交易日 2019.01.01 是周二，每周二交易
            d = date.fromisoformat("2019-01-01")
            # 实际交易日
            dz = date.fromisoformat("2019-01-01")
        
            h_list = KHistory.objects.filter(date__gte=d, trades_tatus=1, stock=s)
            
            for h in h_list:
                
                # 每周二之后交易
                if (h.date - d).days >= 7:
                    
                    max_pe = float(h.maxPE)
                    min_pe = float(h.minPE)
                    pe = float(h.peTTM)
                    pe_range = max_pe - min_pe
            
                    top_pe = max_pe - pe_range * 0.3
                    bottom_pe = min_pe + pe_range * 0.3
            
                    # 交易价格
                    price = float(h.open_price)
                    #print(top_pe, bottom_pe)
            
                    if pe <= bottom_pe:
                        if pe <= min_pe + pe_range * 0.05:
                            c = floor((money * 0.98) / price)
                            s_count += c
                            money -= c*price
                        elif pe <= min_pe + pe_range * 0.10:
                            c = floor((money * 0.93) / price)
                            s_count += c
                            money -= c*price
                        elif pe <= min_pe + pe_range * 0.20:
                            c = floor((money * 0.85) / price)
                            s_count += c
                            money -= c*price
                        elif pe <= min_pe + pe_range * 0.30:
                            c = floor((money * 0.75) / price)
                            s_count += c
                            money -= c*price
                        #print("低估：%s 股票%f 资金%f 交易日%s 交易价格%s" % (h.stock.code_name, s_count, money, h.date, price))
                    elif pe >= top_pe:
                        if pe >= max_pe - pe_range * 0.05:
                            c = s_count*0.95
                            s_count -= c
                            money += c*price
                        elif pe >= max_pe - pe_range * 0.10:
                            c = s_count*0.90
                            s_count -= c
                            money += c*price
                        elif pe >= max_pe - pe_range * 0.20:
                            c = s_count*0.80
                            s_count -= c
                            money += c*price
                        elif pe >= max_pe - pe_range * 0.30:
                            c = s_count*0.70
                            s_count -= c
                            money += c*price
                        #print("高估：%s 股票%f 资金%f 交易日%s 交易价格%s" % (h.stock.code_name, s_count, money, h.date, price))
                
                    # 更新下一次检查日
                    # 调整到下周二
                    d = d + timedelta(days=7)
                    
            print("%s 剩余资金%f 剩余股票%d 股票价值%f === 总价值%f" % (h.stock.code_name, money, s_count, s_count*float(h.open_price), money+s_count*float(h.open_price)))
