# -*- coding:utf-8 -*-
from datetime import date, datetime
import json
import requests
import sys

from django.core.management.base import BaseCommand, CommandError
from stocks.models import Stock, KHistory

import baostock as bs
import pandas as pd

import urllib3
from urllib3 import poolmanager
urllib3.disable_warnings()

class Command(BaseCommand):
    help = '更新证券数据'
    
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

#        my_stocks = ['sz.000651', 'sh.600309', 'sz.000858', 'sh.600030', 'sz.000625', 'sh.600519', 'sh.600085',
#                     'sz.000568', 'sz.000002', 'sh.600015', 'sh.600050', 'sh.600029', 'sh.600010', 'sz.002024', 
#                     'sh.600031', 'sh.600795', 'sz.000063', 'sh.600177', 'sh.600660', 'sh.600104', 'sh.600383', 
#                     'sh.600028', 'sz.000425', 'sz.000768', 'sh.600900', 'sh.600362', 'sh.600019', 'sz.000001', 
#                     'sh.600036', 'sh.600000', 'sh.600196', 'sz.000157', 'sh.600009', 'sz.000538', 'sz.000069', 
#                     'sh.600585', 'sh.600016', 'sh.600741', 'sh.600690']

        #沪深300 sh.000300 sz.399300
        #中证红利 sh.000922
        #50AH优选 sh.000170 拿不到   sh.950090
        #中证500 sh.000905
        #医药100 sh.000978
        #300消费 sh.000912
        #央视50 sz.159965 基金 拿不到
        
        my_stocks = Stock.objects.all()
        #my_stocks = ['sh.950090', 'sz.159965']
        
        my_token = "ab51eeca-033d-4cef-98ed-bbc18c01fad8"
        api_url = "https://open.lixinger.com/api/a/index"
        headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows 98)',
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
        }

        for s in my_stocks:
            if s.ipo_type == 1:
                # 获取证券基本资料
                rs = bs.query_stock_basic(code=s.code)
                # rs = bs.query_stock_basic(code_name="浦发银行")  # 支持模糊查询
                #print('query_stock_basic respond error_code:'+rs.error_code)
                #print('query_stock_basic respond  error_msg:'+rs.error_msg)

                # 打印结果集
                while (rs.error_code == '0') & rs.next():
                    # 获取一条记录，将记录合并在一起
                    x = rs.get_row_data()
                    print(x)
                    try:
                        s.code_name = x[1]
                        s.ipo_date = date(*map(int, x[2].split('-')))
                        s.out_date = None if not x[3] else date(*map(int, x[3].split('-')))
                        s.ipo_type = x[4]
                        s.ipo_status = x[5]
                        s.save()
                    except Exception as e:
                        print(x[0])
                        print(sys.exc_info())
                        print("%s cannot be saved. %s" % (x[0], sys.exc_info()[1]))
            else:
                data = {
                    'token': my_token,
                    "stockCodes": [
                        s.code
                    ]
                }
                
                print(data)
            
                r = requests.post(api_url, data=json.dumps(data), headers=headers, verify=False)
                
                x = json.loads(r.text)
                for p in x.get("data"):
                    print(p)
                    try:
                        s.code_name = p.get('name')
                        s.ipo_date = datetime.fromisoformat(p.get('launchDate').replace('Z', ''))
                        s.save()
                    except Exception as e:
                        print(x[0])
                        print(sys.exc_info())
                        print("%s cannot be saved. %s" % (x[0], sys.exc_info()[1]))
                    
        #### 登出系统 ####
        bs.logout()
