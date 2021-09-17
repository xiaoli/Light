# -*- coding:utf-8 -*-
from datetime import date
import json
import requests
import sys
from datetime import datetime

from django.db.models import Avg, Max, Min
from django.core.management.base import BaseCommand, CommandError
from stocks.models import Stock, KHistory

import urllib3
from urllib3 import poolmanager
urllib3.disable_warnings()

class Command(BaseCommand):
    help = '更新证券的 PE 数据'
    
    def handle(self, *args, **options):
        
        my_token = "ab51eeca-033d-4cef-98ed-bbc18c01fad8"
        
        api_url = "https://open.lixinger.com/api/a/index/fundamental"
        
        headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows 98)',
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
        }

        my_stocks = Stock.objects.all()
        
        today = datetime.today()
        end_date = today.strftime('%Y-%m-%d')

        for stock in my_stocks:
            #### 获取沪深A股历史K线数据 ####
            # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
            # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
            # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
            all_h_set = KHistory.objects.filter(stock=stock).exclude(peTTM=0)
            h_date = all_h_set.order_by('-date').aggregate(Max('date'))
            start_date_from_db = h_date.get('date__max')
            
            start_date = '1990-12-19'
            if start_date_from_db is not None:
                start_date = start_date_from_db.strftime('%Y-%m-%d')
            
            print(stock.code, stock.code_name, start_date, end_date)
            
            if start_date != end_date:
                data = {
                    #'data': {
                        'token': my_token,
                        'startDate': start_date,
                        'endDate': end_date,
                        "stockCodes": [
                        	stock.code[3:]
                        ],
                        "metricsList": [
                        	#"pe_ttm.y10.mcw",
                        	"pe_ttm.mcw",
                        	"mc"
                        ]
                    #}
                }
                
                print(data)
            
                r = requests.post(api_url, data=json.dumps(data), headers=headers, verify=False)
                #print(r.text)
                
                x = json.loads(r.text)
                for p in x.get("data"):
                    print(p.get("date")[:10], p.get("pe_ttm").get("mcw"))
                    try:
                        k = KHistory.objects.get(stock=stock, date=p.get("date")[:10])
                        k.peTTM = p.get("pe_ttm").get("mcw")
                        k.save()
                    except (Stock.DoesNotExist, Exception) as e:
                        print("%s %s cannot be saved. %s" % (x[1], x[0], sys.exc_info()[1]))
                    except Exception as e:
                        pass
