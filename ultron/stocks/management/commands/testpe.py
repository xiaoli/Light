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
        
        total_stocks = 0
        total_money = 0
        
        today = date.today()

        my_stocks = Stock.objects.all()
        print("股票, 低估/高估, 持有股票, 持有资金, 交易日, 交易价格")

        for s in my_stocks:
            
            # 固定成本
            cost = 100000
            # 总起始资本
            money = 100000
            # 持有股票数量
            s_count = 0
            # 开启交易日 2019.01.01 是周二，每周二交易
            d = date.fromisoformat("2019-01-01")
            # 总年份数
            yrs = (today-d).days/365
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
                    price = float(h.open_price.normalize())
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
                        print("%s, 低估, %f, %f, %s, %s" % (h.stock.code_name, s_count, money, h.date, price))
                    elif pe >= top_pe:
                        if pe >= max_pe - pe_range * 0.05:
                            c = floor(s_count*0.95)
                            s_count -= c
                            money += c*price
                        elif pe >= max_pe - pe_range * 0.10:
                            c = floor(s_count*0.90)
                            s_count -= c
                            money += c*price
                        elif pe >= max_pe - pe_range * 0.20:
                            c = floor(s_count*0.80)
                            s_count -= c
                            money += c*price
                        elif pe >= max_pe - pe_range * 0.30:
                            c = floor(s_count*0.70)
                            s_count -= c
                            money += c*price
                        print("%s, 高估, %f, %f, %s, %s" % (h.stock.code_name, s_count, money, h.date, price))
                
                    # 更新下一次检查日
                    # 调整到下周二
                    d = d + timedelta(days=7)
                    
            print("===投资结果===")
            print("%s 剩余资金%f 剩余股票%d 股票价值%f === 总价值%f" % (h.stock.code_name, money, s_count, s_count*price, money+s_count*price))
            print("%s 绝对收益%s 复合年化收益率%s " % (h.stock.code_name, "{:.2%}".format(((money+s_count*price)/cost-1)), "{:.2%}".format((pow((money+s_count*price)/cost, 1/yrs)-1))) )
            print("")
            total_money += money
            total_stocks += s_count
            
        print("===总投资结果===")
        # 总价值
        all_value = total_money+total_stocks*price
        # 总成本
        all_cost = cost*my_stocks.count()
        print("总投入%f 总剩余资金%f 总剩余股票%f 总股票价值%f === 总价值%f" % (cost*my_stocks.count(), total_money, total_stocks, total_stocks*price, all_value) )
        print("总绝对收益%s 总复合年化收益率%s " % ("{:.2%}".format(all_value/all_cost - 1), "{:.2%}".format((pow(all_value/all_cost, 1/yrs)-1))) )
