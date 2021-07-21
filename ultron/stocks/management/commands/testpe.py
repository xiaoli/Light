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
import numpy as np

class Command(BaseCommand):
    help = '回溯测试'
    
    def handle(self, *args, **options):
        
        def MaxDrawdown(return_list):
            # 1. find all of the peak of cumlative return 
            maxcum = np.zeros(len(return_list))
            b = return_list[0]
            for i in range(0,len((return_list))):
                if (return_list[i]>b):
                    b = return_list[i]
                maxcum[i] = b
    
            # 2. then find the max drawndown point
            i = np.argmax((np.maximum.accumulate(return_list)- return_list)/np.maximum.accumulate(return_list))
            if i == 0:
                return 0
            j = np.argmax(return_list[:i])
        
            # 3. return the maxdrawndown
            return(return_list[j] - return_list[i]) / return_list[j],j,i
        
        #### 四个关注指标 ####
        # close 当日收盘价
        # peTTM 滚动市盈率
        
        total_stocks = 0
        total_money = 0
        total_stocks_value = 0
        
        today = date.today()

        #my_stocks = Stock.objects.filter(code='sh.000300')
        my_stocks = Stock.objects.all()
        print("股票, 日期, 低估/高估, 具体分档, P/E, Max P/E, Min P/E, 当日股价, 股持仓, 股价值, 现金, 股比例, 现金比例, 总价值")

        for s in my_stocks:
            
            # 固定成本
            cost = 10000000
            # 总起始资本
            money = 10000000
            # 持有股票数量
            s_count = 0
            # 开启交易日 2019.01.01 是周二，每周二交易
            d = date.fromisoformat("2019-01-01")
            # 总年份数
            yrs = (today-d).days/365
            # 实际交易日
            dz = date.fromisoformat("2019-01-01")
            
            # 回撤的资产list
            draw_value_list = []
            # 回撤的日期list
            draw_date_list = []
        
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
                    
                    # 当日开盘总资产
                    day_value = money+s_count*price
                    
                    # PE 档位
                    pe_rank = ''
            
                    if pe <= bottom_pe:
                        if pe <= min_pe + pe_range * 0.05:
                            pe_rank = '后5%及以上'
                            c = floor((day_value * 0.98) / price)
                            if c > s_count:
                                money -= (c-s_count)*price
                                s_count += (c-s_count)
                            else:
                                money += (s_count-c)*price
                                s_count -= (s_count-c)
                                
                        elif pe <= min_pe + pe_range * 0.10:
                            pe_rank = '后10%至5%'
                            c = floor((day_value * 0.93) / price)
                            if c > s_count:
                                money -= (c-s_count)*price
                                s_count += (c-s_count)
                            else:
                                money += (s_count-c)*price
                                s_count -= (s_count-c)
                            
                        elif pe <= min_pe + pe_range * 0.20:
                            pe_rank = '后20%至10%'
                            c = floor((day_value * 0.85) / price)
                            if c > s_count:
                                money -= (c-s_count)*price
                                s_count += (c-s_count)
                            else:
                                money += (s_count-c)*price
                                s_count -= (s_count-c)
                                
                        elif pe <= min_pe + pe_range * 0.30:
                            pe_rank = '后30%至20%'
                            c = floor((day_value * 0.75) / price)
                            if c > s_count:
                                money -= (c-s_count)*price
                                s_count += (c-s_count)
                            else:
                                money += (s_count-c)*price
                                s_count -= (s_count-c)
                                
                        # 当日收盘总资产
                        day_value = money+s_count*price
                        print("%s, %s, 低, %s, %f, %f, %f, %s, %s, %s, %s, %s, %s, %s" % (h.stock.code_name, h.date, pe_rank, h.peTTM, h.maxPE, h.minPE, price, s_count, price*s_count, money,  "{:.2%}".format((price*s_count)/day_value), "{:.2%}".format(money/day_value), day_value))
                        draw_value_list.append(money+s_count*price)
                        draw_date_list.append(h.date)
                        
                    elif pe >= top_pe:
                        if pe >= max_pe - pe_range * 0.05:
                            pe_rank = '前5%及以上'
                            c = floor((day_value * 0.05) / price)
                            #print(c, day_value, "=========1")
                            if c < s_count:
                                money += (s_count-c)*price
                                s_count -= (s_count-c)
                            else:
                                money -= (c-s_count)*price
                                s_count += (c-s_count)
                                
                        elif pe >= max_pe - pe_range * 0.10:
                            pe_rank = '前10%至5%'
                            c = floor((day_value * 0.10) / price)
                            #print(c, day_value, "=========2")
                            if c < s_count:
                                money += (s_count-c)*price
                                s_count -= (s_count-c)
                            else:
                                money -= (c-s_count)*price
                                s_count += (c-s_count)
                            
                        elif pe >= max_pe - pe_range * 0.20:
                            pe_rank = '前20%至10%'
                            c = floor((day_value * 0.20) / price)
                            #print(c, day_value, "=========3")
                            if c < s_count:
                                money += (s_count-c)*price
                                s_count -= (s_count-c)
                            else:
                                money -= (c-s_count)*price
                                s_count += (c-s_count)
                                
                        elif pe >= max_pe - pe_range * 0.30:
                            pe_rank = '前30%至20%'
                            c = floor((day_value * 0.30) / price)
                            #print(c, day_value, day_value*0.70, floor(day_value*0.70), "=========4")
                            if c < s_count:
                                money += (s_count-c)*price
                                s_count -= (s_count-c)
                            else:
                                money -= (c-s_count)*price
                                s_count += (c-s_count)
                                
                        # 当日收盘总资产
                        day_value = money+s_count*price
                        print("%s, %s, 高, %s, %f, %f, %f, %s, %s, %s, %s, %s, %s, %s" % (h.stock.code_name, h.date, pe_rank, h.peTTM, h.maxPE, h.minPE, price, s_count, price*s_count, money,  "{:.2%}".format((price*s_count)/day_value), "{:.2%}".format(money/day_value), day_value))
                        draw_value_list.append(day_value)
                        draw_date_list.append(h.date)
                        
                    else:
                        # 当日收盘总资产
                        day_value = money+s_count*price
                        pe_rank = '无档位'
                        print("%s, %s, 无变化, %s, %f, %f, %f, %s, %s, %s, %s, %s, %s, %s" % (h.stock.code_name, h.date, pe_rank, h.peTTM, h.maxPE, h.minPE, price, s_count, price*s_count, money,  "{:.2%}".format((price*s_count)/day_value), "{:.2%}".format(money/day_value), day_value))
                    # 更新下一次检查日
                    # 调整到下周二
                    d = d + timedelta(days=7)
                    #print(c, "==========")
                    
            print("===投资结果===")
            print("%s 剩余资金%f 剩余股票%d 股票价值%f === 总价值%f" % (h.stock.code_name, money, s_count, s_count*price, money+s_count*price))
            print("%s 绝对收益%s 复合年化收益率%s " % (h.stock.code_name, "{:.2%}".format(((money+s_count*price)/cost-1)), "{:.2%}".format((pow((money+s_count*price)/cost, 1/yrs)-1))) )
            
            drawndown,startdate,enddate = MaxDrawdown(draw_value_list)
            print( "%s 最大回撤%s 开始日期%s 结束日期%s" % ( h.stock.code_name, "{:.2%}".format(drawndown), draw_date_list[startdate], draw_date_list[enddate]) )
            
            print("")
            total_money += money
            total_stocks += s_count
            total_stocks_value += price * s_count
            
        print("===总投资结果===")
        # 总价值
        all_value = total_money+total_stocks_value
        # 总成本
        all_cost = cost*my_stocks.count()
        print("总投入%f 总剩余资金%f 总剩余股票%f 总股票价值%f === 总价值%f" % (all_cost, total_money, total_stocks, total_stocks_value, all_value) )
        print("总绝对收益%s 总复合年化收益率%s " % ("{:.2%}".format(all_value/all_cost - 1), "{:.2%}".format((pow(all_value/all_cost, 1/yrs)-1))) )
