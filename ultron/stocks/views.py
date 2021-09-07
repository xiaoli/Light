from django.shortcuts import render
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Max, Min, Avg
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.shortcuts import get_object_or_404

import json
import datetime
import requests

from datetime import date, timedelta
import json
import requests
from math import floor
import numpy as np

from django.core.management.base import BaseCommand, CommandError

from .models import Stock, KHistory, Strategy, Rule
from .serializers import json_serialize

@login_required(login_url='/admin/login/')
def index(request):
    s_list = Stock.objects.all()
    
    template = loader.get_template('index.html')

    context = {
        's_list': s_list,
        'user': request.user
    }
    return HttpResponse(template.render(context, request))
    
@login_required(login_url='/admin/login/')
@csrf_exempt
def get_history_by_stock(request):
    sid = request.GET['sid']
    
    s = Stock.objects.get(pk=sid)
    h_list = KHistory.objects.filter(stock=s)
    
    data = []
    for h in h_list:
        data.append({
            'date': h.date,
            'open': h.open_price,
            'low': h.low_price,
            'high': h.high_price,
            'close': h.close_price,
            'pe': h.peTTM,
            'pb': h.pbMRQ,
            'volume': h.volume
        })
    
    #json_data = json_serialize(h_list, fields=('id', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'preclose_price', 
    #                'volume', 'amount', 'adjust_flag', 'turn', 'trades_tatus', 'pctChg', 'peTTM', 'psTTM', 'pcfNcfTTM',
    #                'pbMRQ', 'is_st'))
    
    return JsonResponse(data, safe=False)
    
@login_required(login_url='/admin/login/')
@csrf_exempt
def get_history_by_date(request):
    data = json.loads(request.body)
    
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    s = Stock.objects.get(pk=data.get('sid'))
    h_list = KHistory.objects.filter(date__range=[start_date, end_date], stock=s)
    
    json_data = json_serialize(h_list, fields=('id', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'preclose_price', 
                    'volume', 'amount', 'adjust_flag', 'turn', 'trades_tatus', 'pctChg', 'peTTM', 'psTTM', 'pcfNcfTTM',
                    'pbMRQ', 'is_st'))  
           
    qs = KHistory.objects.filter(stock=s)         
    maxPe = qs.aggregate(Max('peTTM')).get('peTTM__max')
    minPe = qs.aggregate(Min('peTTM')).get('peTTM__min')
    maxPb = qs.aggregate(Max('pbMRQ')).get('pbMRQ__max')
    minPb = qs.aggregate(Min('pbMRQ')).get('pbMRQ__min')
                    
    #data = {
    #    'pe': [minPe, maxPe],
    #    'pb': [minPb, maxPb],
    #    'history': json_data
    #}
    
    return JsonResponse(json_data, safe=False)

@login_required(login_url='/admin/login/')
def list_strategy(request):
    my_strategies = Strategy.objects.filter(available=1)
    
    template = loader.get_template('list_strategy.html')

    context = {
        's_list': my_strategies,
        'user': request.user
    }
    return HttpResponse(template.render(context, request))    

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

@login_required(login_url='/admin/login/')
def calculate(request):
    sid = request.GET.get('sid', 1)
    strategy = get_object_or_404(Strategy, pk=sid)
    
    str_list = []
    
    str_list.append("===========================")
    str_list.append("          策略：%s          " % strategy.name)
    str_list.append("===========================")
    
    high_rules = Rule.objects.filter(strategy=strategy, operation=2, available=1).order_by('-priority')
    low_rules = Rule.objects.filter(strategy=strategy, operation=1, available=1).order_by('-priority')

    #### 四个关注指标 ####
    # close 当日收盘价
    # peTTM 滚动市盈率

    total_stocks = 0
    total_money = 0
    total_stocks_value = 0

    today = date.today()

    #my_stocks = Stock.objects.filter(code='sh.000300')
    # 所有股票
    #my_stocks = Stock.objects.all()
    
    # 仅限选中股票
    my_stocks = strategy.stocks.all()
    
    str_list.append("股票, 日期, 低估/高估, 具体分档, P/E, Max P/E, Min P/E, 当日股价, 股持仓, 股价值, 现金, 股比例, 现金比例, 总价值")

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
            
                # 均值策略(默认)
                max_pe = float(h.maxPE)
                min_pe = float(h.minPE)
                
                # MM策略
                if strategy.s_type is 1:
                    max_pe = float(h.avgMaxPE)
                    min_pe = float(h.avgMinPE)
                    
                pe = float(h.peTTM)
                pe_range = max_pe - min_pe
    
                top_pe = max_pe - pe_range * (strategy.top_limit/100)
                bottom_pe = min_pe + pe_range * (strategy.bottom_limit/100)
    
                # 交易价格
                price = float(h.open_price.normalize())
                #str_list.append(top_pe, bottom_pe)
            
                # 当日开盘总资产
                day_value = money+s_count*price
            
                # PE 档位
                pe_rank = ''
    
                if pe <= bottom_pe:
                    
                    for r in low_rules:
                        if pe <= min_pe + pe_range * (r.limit/100):
                            c = floor((day_value * (r.holding/100)) / price)
                            if c > s_count:
                                money -= (c-s_count)*price
                                s_count += (c-s_count)
                            else:
                                money += (s_count-c)*price
                                s_count -= (s_count-c)
                                
                            break # 只要有一条 rule 符合判断，那就退出整个 rule 循环
                        
                    # 当日收盘总资产
                    day_value = money+s_count*price
                    str_list.append("%s, %s, 低, %s, %f, %f, %f, %s, %s, %s, %s, %s, %s, %s" % (h.stock.code_name, h.date, pe_rank, h.peTTM, h.maxPE, h.minPE, price, s_count, price*s_count, money,  "{:.2%}".format((price*s_count)/day_value), "{:.2%}".format(money/day_value), day_value))
                    draw_value_list.append(money+s_count*price)
                    draw_date_list.append(h.date)
                
                elif pe >= top_pe:
                    
                    for r in high_rules:
                        if pe >= max_pe - pe_range * (r.limit/100):
                            c = floor((day_value * (r.holding/100)) / price)
                            if c < s_count:
                                money += (s_count-c)*price
                                s_count -= (s_count-c)
                            else:
                                money -= (c-s_count)*price
                                s_count += (c-s_count)
                                
                            break # 只要有一条 rule 符合判断，那就退出整个 rule 循环
                        
                    # 当日收盘总资产
                    day_value = money+s_count*price
                    str_list.append("%s, %s, 高, %s, %f, %f, %f, %s, %s, %s, %s, %s, %s, %s" % (h.stock.code_name, h.date, pe_rank, h.peTTM, h.maxPE, h.minPE, price, s_count, price*s_count, money,  "{:.2%}".format((price*s_count)/day_value), "{:.2%}".format(money/day_value), day_value))
                    draw_value_list.append(day_value)
                    draw_date_list.append(h.date)
                
                else:
                    # 当日收盘总资产
                    day_value = money+s_count*price
                    pe_rank = '无档位'
                    str_list.append("%s, %s, 无变化, %s, %f, %f, %f, %s, %s, %s, %s, %s, %s, %s" % (h.stock.code_name, h.date, pe_rank, h.peTTM, h.maxPE, h.minPE, price, s_count, price*s_count, money,  "{:.2%}".format((price*s_count)/day_value), "{:.2%}".format(money/day_value), day_value))
                # 更新下一次检查日
                # 调整到下周二
                d = d + timedelta(days=7)
                #str_list.append(c, "==========")
            
        str_list.append("===投资结果===")
        str_list.append("%s 剩余资金%f 剩余股票%d 股票价值%f === 总价值%f" % (h.stock.code_name, money, s_count, s_count*price, money+s_count*price))
        str_list.append("%s 绝对收益%s 复合年化收益率%s " % (h.stock.code_name, "{:.2%}".format(((money+s_count*price)/cost-1)), "{:.2%}".format((pow((money+s_count*price)/cost, 1/yrs)-1))) )
    
        drawndown,startdate,enddate = MaxDrawdown(draw_value_list)
        str_list.append( "%s 最大回撤%s 开始日期%s 结束日期%s" % ( h.stock.code_name, "{:.2%}".format(drawndown), draw_date_list[startdate], draw_date_list[enddate]) )
    
        str_list.append("")
        total_money += money
        total_stocks += s_count
        total_stocks_value += price * s_count
    
    str_list.append("===总投资结果===")
    # 总价值
    all_value = total_money+total_stocks_value
    # 总成本
    all_cost = cost*my_stocks.count()
    str_list.append("总投入%f 总剩余资金%f 总剩余股票%f 总股票价值%f === 总价值%f" % (all_cost, total_money, total_stocks, total_stocks_value, all_value) )
    str_list.append("总绝对收益%s 总复合年化收益率%s " % ("{:.2%}".format(all_value/all_cost - 1), "{:.2%}".format((pow(all_value/all_cost, 1/yrs)-1))) )
    
    
    template = loader.get_template('calculate.html')

    context = {
        'str_list': str_list,
        'user': request.user
    }
    return HttpResponse(template.render(context, request))