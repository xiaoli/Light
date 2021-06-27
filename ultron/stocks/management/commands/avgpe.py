# -*- coding:utf-8 -*-
from datetime import date
import json
import requests

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Avg, Max, Min
from stocks.models import Stock, KHistory

import baostock as bs
import pandas as pd

class Command(BaseCommand):
    help = '计算近十年滚动PE'
    
    def handle(self, *args, **options):
        
        #### 四个关注指标 ####
        # close 当日收盘价
        # peTTM 滚动市盈率
        
        money = 100000

        my_stocks = Stock.objects.all()

        for s in my_stocks:
            h_list = KHistory.objects.filter(date__gte="2019-01-01", stock=s)
            print(h_list.count())
            for h in h_list:
                print(h.date)
                end_date = h.date#date.fromisoformat(h.date)
                start_date = end_date.replace( year = end_date.year - 10 )
                avg_pe = KHistory.objects.filter(date__gte=start_date, date__lt=end_date, stock=s).aggregate(Avg('peTTM'))
                print(avg_pe.get('peTTM__avg'))
                
                p = avg_pe.get('peTTM__avg')
                
                h.avg_pe = p
                h.save()
                
                if p > float(h.peTTM):
                    print("低估")
                    
                elif p < float(h.peTTM):
                    print("高估")
