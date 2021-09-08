# -*- coding:utf-8 -*-
from datetime import date
import json
import requests

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Avg, Max, Min, Sum
from stocks.models import Stock, KHistory

import baostock as bs
import pandas as pd

class Command(BaseCommand):
    help = '计算近十年滚动PE'
    
    def handle(self, *args, **options):
        
        #### 四个关注指标 ####
        # close 当日收盘价
        # peTTM 滚动市盈率

        my_stocks = Stock.objects.all()

        for s in my_stocks:
            # avgPE__isnull=True 仅计算未计算过的数据
            h_list = KHistory.objects.filter(date__gte="2019-01-01", stock=s, avgPE__isnull=True)
            
            print(h_list.count())
            for h in h_list:
                print(h.date)
                end_date = h.date#date.fromisoformat(h.date)
                start_date = end_date.replace( year = end_date.year - 10 )
                
                all_pe_set = KHistory.objects.filter(date__gte=start_date, date__lt=end_date, stock=s).exclude(peTTM=0)
                percent_count = int(all_pe_set.count() * 0.3)
                
                # MM策略所需
                pe = all_pe_set.aggregate(Avg('peTTM'), Max('peTTM'), Min('peTTM'))
                h.maxPE = pe.get('peTTM__max')
                h.minPE = pe.get('peTTM__min')
                h.avgPE = pe.get('peTTM__avg')
                
                # 均值策略所需
                h_pe = all_pe_set.order_by('-peTTM')[:percent_count].aggregate(Sum('peTTM'))
                l_pe = all_pe_set.order_by('peTTM')[:percent_count].aggregate(Sum('peTTM'))
                h.avgMaxPE = h_pe.get('peTTM__sum') / percent_count
                h.avgMinPE = l_pe.get('peTTM__sum') / percent_count
                
                print(h.avgPE, h.maxPE, h.avgMaxPE, h.minPE, h.avgMinPE)
                
                h.save()
                