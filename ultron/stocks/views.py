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
    s_list = Stock.objects.filter(ipo_type=2)
    r_list = []
    
    year = 10
    
    for s in s_list:
        kh = KHistory.objects.filter(stock=s).exclude(peTTM=0).exclude(peTTM__isnull=True).exclude(metrics_value=u'').exclude(metrics_value__isnull=True).order_by('-date')[0]
        metrics_value = json.loads(kh.metrics_value)
        pe_list = metrics_value.get("Y%s" % year)
        if pe_list and len(pe_list) > 0:
            s.h_pe = pe_list.get("h_pe_list")[-1]
            s.l_pe = pe_list.get("l_pe_list")[-1]
        s.pe_date = kh.date
        s.pe_value = kh.peTTM
        
        r_list.append(s)
        #print(metrics_value.get("Y%s" % year).get("h_pe_list"), metrics_value.get("Y%s" % year).get("l_pe_list"))
    
    template = loader.get_template('list_report.html')

    context = {
        's_list': r_list,
        'user': request.user
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url='/admin/login/')
def stock_index(request):
    s_list = Stock.objects.filter(ipo_type=1)
    r_list = []
    
    year = 10
    
    for s in s_list:
        kh = KHistory.objects.filter(stock=s).exclude(peTTM=0).exclude(peTTM__isnull=True).exclude(metrics_value=u'').exclude(metrics_value__isnull=True).order_by('-date')[0]
        metrics_value = json.loads(kh.metrics_value)
        pe_list = metrics_value.get("Y%s" % year)
        if pe_list and len(pe_list) > 0:
            s.h_pe = pe_list.get("h_pe_list")[-1]
            s.l_pe = pe_list.get("l_pe_list")[-1]
        s.pe_date = kh.date
        s.pe_value = kh.peTTM
        
        r_list.append(s)
        #print(metrics_value.get("Y%s" % year).get("h_pe_list"), metrics_value.get("Y%s" % year).get("l_pe_list"))
    
    template = loader.get_template('list_report.html')

    context = {
        's_list': r_list,
        'user': request.user
    }
    return HttpResponse(template.render(context, request))
    
@login_required(login_url='/admin/login/')
def list_all_report(request):
    sid = request.GET['sid']
    
    s = Stock.objects.get(pk=sid)
    h_list = KHistory.objects.filter(stock=s).exclude(peTTM=0).exclude(peTTM__isnull=True).exclude(metrics_value=u'').exclude(metrics_value__isnull=True).order_by('-date')

    r_list = []
    year = 10
    
    for h in h_list:
        metrics_value = json.loads(h.metrics_value)
        pe_list = metrics_value.get("Y%s" % year)
        if pe_list and len(pe_list) > 0:
            h.h_pe = pe_list.get("h_pe_list")[-1]
            h.l_pe = pe_list.get("l_pe_list")[-1]
        h.pe_date = h.date
        h.pe_value = h.peTTM
        
        r_list.append(h)
    
    template = loader.get_template('list_all_report.html')

    context = {
        'r_list': r_list,
        'user': request.user
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url='/admin/login/')
def list_khistory(request):
    s_list = Stock.objects.all()
    
    template = loader.get_template('list_khistory.html')

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
        return 0,0,0
    j = np.argmax(return_list[:i])

    # 3. return the maxdrawndown
    return(return_list[j] - return_list[i]) / return_list[j],j,i

@login_required(login_url='/admin/login/')
def calculate(request):
    # 策略ID
    sid = request.GET.get('sid', 1)
    # 考察年份
    year = request.GET.get('year', 10)
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
        
        # 当日收盘价
        price = 0

        
        h_list = KHistory.objects.filter(date__gte=d, trades_tatus=1, stock=s).exclude(peTTM=0).exclude(peTTM__isnull=True).exclude(metrics_value=u'').exclude(metrics_value__isnull=True)
    
        for h in h_list:
            metrics_value = json.loads(h.metrics_value)
            
            # 交易价格 @20211005 改为收盘价
            price = float(h.close_price.normalize())
        
            # 每周二之后交易
            if (h.date - d).days >= 7:
            
                # 均值策略(默认)
                max_pe = float(metrics_value.get("Y%s" % year).get("maxPE"))
                min_pe = float(metrics_value.get("Y%s" % year).get("minPE"))
                
                # MM策略
                if strategy.s_type == 2:
                    max_pe = float(metrics_value.get("Y%s" % year).get("avgMaxPE"))
                    min_pe = float(metrics_value.get("Y%s" % year).get("avgMinPE"))
                    
                pe = float(h.peTTM)
                pe_range = max_pe - min_pe
    
                top_pe = max_pe - pe_range * (strategy.top_limit/100)
                bottom_pe = min_pe + pe_range * (strategy.bottom_limit/100)
                
                # 均值策略V1
                # t 由高到低
                # b 由低到高
                if strategy.s_type == 3:
                    
                    t = metrics_value.get("Y%s" % year).get("h_pe_list")[:strategy.top_limit]
                    b = metrics_value.get("Y%s" % year).get("l_pe_list")[:strategy.bottom_limit]
                    #top_pe = sum([float(i) for i in t])/strategy.top_limit
                    #bottom_pe = sum([float(i) for i in b])/strategy.bottom_limit
                    top_pe = t[strategy.top_limit-1]
                    bottom_pe = b[strategy.bottom_limit-1]
                    #print("==H==", h.date, top_pe, strategy.top_limit)
                    #print("==L==", h.date, bottom_pe, strategy.bottom_limit)
                    
                    max_pe = metrics_value.get("Y%s" % year).get("h_pe_list")[0]
                    min_pe = metrics_value.get("Y%s" % year).get("l_pe_list")[0]
                    #print("=MAX=", max_pe, min_pe)
                    
                    # b 改成由高到低
                    #metrics_value.get("Y%s" % year).get("h_pe_list").reverse()
                    #metrics_value.get("Y%s" % year).get("l_pe_list").reverse()
    
                #str_list.append(top_pe, bottom_pe)
            
                # 当日开盘总资产
                day_value = money+s_count*price
            
                # PE 档位
                pe_rank = ''
    
                # 均值策略 或 MM策略
                if strategy.s_type != 3:
                    # 低估时
                    if pe <= bottom_pe:
                        for r in low_rules:
                            if pe <= min_pe + pe_range * (r.limit/100):
                                pe_rank = r.name
                                # 计算出需要持有的股票数c
                                c = floor((day_value * (r.holding/100)) / price)
                                # 如果需要持有的股票数c大于现在持有的股票数s_count
                                if c > s_count:
                                    money -= (c-s_count)*price
                                    s_count += (c-s_count)
                                # @20211004 低估只有买入，高估只有卖出    
                                #else:
                                #    money += (s_count-c)*price
                                #    s_count -= (s_count-c)
                            
                                break # 只要有一条 rule 符合判断，那就退出整个 rule 循环
                        
                        # 当日收盘总资产
                        day_value = money+s_count*price
                        str_list.append("%s, %s, 低, %s, %f, %f, %f, %s, %s, %s, %s, %s, %s, %s" % (h.stock.code_name, h.date, pe_rank, h.peTTM, max_pe, min_pe, price, s_count, price*s_count, money,  "{:.2%}".format((price*s_count)/day_value), "{:.2%}".format(money/day_value), day_value))
                        draw_value_list.append(day_value)
                        draw_date_list.append(h.date)
                        
                    # 高估时
                    elif pe >= top_pe:
                        for r in high_rules:
                            if pe >= max_pe - pe_range * (r.limit/100):
                                pe_rank = r.name
                                c = floor((day_value * (r.holding/100)) / price)
                                if c < s_count:
                                    money += (s_count-c)*price
                                    s_count -= (s_count-c)
                                # @20211004 低估只有买入，高估只有卖出
                                #else:
                                #    money -= (c-s_count)*price
                                #    s_count += (c-s_count)
                            
                                break # 只要有一条 rule 符合判断，那就退出整个 rule 循环
                            
                        # 当日收盘总资产
                        day_value = money+s_count*price
                        str_list.append("%s, %s, 高, %s, %f, %f, %f, %s, %s, %s, %s, %s, %s, %s" % (h.stock.code_name, h.date, pe_rank, h.peTTM, max_pe, min_pe, price, s_count, price*s_count, money,  "{:.2%}".format((price*s_count)/day_value), "{:.2%}".format(money/day_value), day_value))
                        draw_value_list.append(day_value)
                        draw_date_list.append(h.date)
                
                    else:
                        # 当日收盘总资产
                        day_value = money+s_count*price
                        pe_rank = '无档位'
                        str_list.append("%s, %s, 无变化, %s, %f, %f, %f, %s, %s, %s, %s, %s, %s, %s" % (h.stock.code_name, h.date, pe_rank, h.peTTM, max_pe, min_pe, price, s_count, price*s_count, money,  "{:.2%}".format((price*s_count)/day_value), "{:.2%}".format(money/day_value), day_value))
                
                # 均值策略V1
                else:
                    if pe <= bottom_pe:
                        last_b_limit = 0 # 上一次的估值区间
                        flag_b_action = False # 是否执行过卖出操作
                        for r in low_rules:
                            
                            #取平均值
                            #b = metrics_value.get("Y%s" % year).get("l_pe_list")[last_b_limit:r.limit]
                            
                            #直接取点值
                            b = metrics_value.get("Y%s" % year).get("l_pe_list")[r.limit-1]
                            
                            #print(h.date, "低", r.limit, b, metrics_value.get("Y%s" % year).get("l_pe_list")[:30])
                            #print(h.date, '低%d-%d' % (last_b_limit, r.limit), b, pe, sum([float(i) for i in b])/(r.limit-last_b_limit))
                            
                            #取平均值
                            #if pe <= sum([float(i) for i in b])/(r.limit-last_b_limit):
                            
                            #取点值
                            if pe <= b:
                                pe_rank = r.name
                                c = floor((day_value * (r.holding/100)) / price)
                                if c > s_count:
                                    money -= (c-s_count)*price
                                    s_count += (c-s_count)
                                
                                # @20211004 低估只有买入，高估只有卖出
                                #else:
                                #    money += (s_count-c)*price
                                #    s_count -= (s_count-c)
                                
                                    last_b_limit = r.limit # 收紧为上一次的估值区间
                                    flag_b_action = True
                                break # 只要有一条 rule 符合判断，那就退出整个 rule 循环
                        
                        # 当日收盘总资产
                        day_value = money+s_count*price
                        if not pe_rank:
                            pe_rank = '无规则匹配'
                        str_list.append("%s, %s, 低, %s, %f, %f, %f, %s, %s, %s, %s, %s, %s, %s" % (h.stock.code_name, h.date, pe_rank, h.peTTM, max_pe, min_pe, price, s_count, price*s_count, money,  "{:.2%}".format((price*s_count)/day_value), "{:.2%}".format(money/day_value), day_value))
                        # 只有操作了，才能记录下回撤
                        if flag_b_action:
                            draw_value_list.append(day_value)
                            draw_date_list.append(h.date)
                        
                    elif pe >= top_pe:
                        last_t_limit = 0 # 上一次的估值区间
                        flag_t_action = False # 是否执行过买入操作
                        for r in high_rules:
                            # 取平均值
                            t = metrics_value.get("Y%s" % year).get("h_pe_list")[last_t_limit:r.limit]
                            #print(h.date, "高", pe, r.limit, sum([float(i) for i in t])/(len(t)), metrics_value.get("Y%s" % year).get("h_pe_list")[:30])
                            # 取点值
                            #t = metrics_value.get("Y%s" % year).get("h_pe_list")[r.limit-1]
                            #print(h.date, '高%d-%d' % (last_t_limit, r.limit), t, pe, sum([float(i) for i in t])/(r.limit-last_t_limit))
                            # 平均值判定
                            if pe >= sum([float(i) for i in t])/(len(t)):
                            # 点值判定
                            #if pe >= t:
                                pe_rank = r.name
                                c = floor((day_value * (r.holding/100)) / price)
                                if c < s_count:
                                    money += (s_count-c)*price
                                    s_count -= (s_count-c)
                                # @20211004 低估只有买入，高估只有卖出
                                #else:
                                #    money -= (c-s_count)*price
                                #    s_count += (c-s_count)
                            
                                    last_t_limit = r.limit # 收紧为上一次的估值区间
                                    flag_t_action = True
                                break # 只要有一条 rule 符合判断，那就退出整个 rule 循环
                            
                        # 当日收盘总资产
                        #
                        day_value = money+s_count*price
                        if not pe_rank:
                            pe_rank = '无规则匹配'
                        str_list.append("%s, %s, 高, %s, %f, %f, %f, %s, %s, %s, %s, %s, %s, %s" % (h.stock.code_name, h.date, pe_rank, h.peTTM, max_pe, min_pe, price, s_count, price*s_count, money,  "{:.2%}".format((price*s_count)/day_value), "{:.2%}".format(money/day_value), day_value))
                        if flag_t_action:
                            draw_value_list.append(day_value)
                            draw_date_list.append(h.date)
                
                    else:
                        # 当日收盘总资产
                        #print(h.date, "无档位", pe, top_pe, bottom_pe, max_pe, min_pe)
                        day_value = money+s_count*price
                        pe_rank = '无档位'
                        str_list.append("%s, %s, 无变化, %s, %f, %f, %f, %s, %s, %s, %s, %s, %s, %s" % (h.stock.code_name, h.date, pe_rank, h.peTTM, max_pe, min_pe, price, s_count, price*s_count, money,  "{:.2%}".format((price*s_count)/day_value), "{:.2%}".format(money/day_value), day_value))
                
                # 更新下一次检查日
                # 调整到下周二
                d = d + timedelta(days=7)
                #str_list.append(c, "==========")    
        
        str_list.append("===投资结果===")
        str_list.append("%s 剩余资金%f 剩余股票%d 股票价值%f === 总价值%f" % (h.stock.code_name, money, s_count, s_count*price, money+s_count*price))
        str_list.append("%s 绝对收益%s 复合年化收益率%s " % (h.stock.code_name, "{:.2%}".format(((money+s_count*price)/cost-1)), "{:.2%}".format((pow((money+s_count*price)/cost, 1/yrs)-1))) )
        
        # 如果没有包含值，就不要计算回撤了
        if draw_value_list:
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