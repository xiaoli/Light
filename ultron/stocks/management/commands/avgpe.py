# -*- coding:utf-8 -*-
from datetime import date
import simplejson as json
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
            # metrics_value__isnull=True 仅计算未计算过的数据
            h_list = KHistory.objects.filter(date__gte="2019-01-01", stock=s, metrics_value__isnull=True)
            
            print(h_list.count())
            for h in h_list:
                print(h.date, h.id)
                end_date = h.date#date.fromisoformat(h.date)
                
                # 保存至数据库的所有数据
                json_value_list = {}
                for i in range(1, 11):
                    # 当前年份下的数据
                    current_year = {}
                    
                    start_date = end_date.replace( year = end_date.year - i )

                    all_pe_set = KHistory.objects.filter(date__gte=start_date, date__lt=end_date, stock=s).exclude(peTTM=0)
                    
                    # MM策略所需
                    pe = all_pe_set.aggregate(Avg('peTTM'), Max('peTTM'), Min('peTTM'))
                    current_year["maxPE"] = pe.get('peTTM__max')
                    current_year["minPE"] = pe.get('peTTM__min')
                    current_year["avgPE"] = pe.get('peTTM__avg')
                
                    # 均值策略所需
                    percent_count = int(all_pe_set.count() * 0.3)
                    h_pe = all_pe_set.order_by('-peTTM')[:percent_count].aggregate(Sum('peTTM'))
                    l_pe = all_pe_set.order_by('peTTM')[:percent_count].aggregate(Sum('peTTM'))
                    current_year["avgMaxPE"] = h_pe.get('peTTM__sum') / percent_count
                    current_year["avgMinPE"] = l_pe.get('peTTM__sum') / percent_count
                
                    # 均值策略v1版所需
                    current_year["h_pe_list"] = []
                    current_year["l_pe_list"] = []
                    for x in range(0, 30):
                        h_pe = all_pe_set.order_by('-peTTM')[int(all_pe_set.count() * x * 0.01):int(all_pe_set.count() * (x+1) * 0.01)].aggregate(Sum('peTTM'))
                        current_year["h_pe_list"].append( h_pe.get('peTTM__sum') / int(all_pe_set.count() * 0.01) )
                        l_pe = all_pe_set.order_by('peTTM')[int(all_pe_set.count() * x * 0.01):int(all_pe_set.count() * (x+1) * 0.01)].aggregate(Sum('peTTM'))
                        current_year["l_pe_list"].append( l_pe.get('peTTM__sum') / int(all_pe_set.count() * 0.01) )
                    
                    json_value_list["Y%s" % i] = current_year
                
                h.metrics_value = json.dumps(json_value_list, use_decimal=True)
                #print(h.metrics_value)
                h.save()
                