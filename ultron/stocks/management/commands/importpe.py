# -*- coding:utf-8 -*-
from datetime import date
import json
import requests

from django.core.management.base import BaseCommand, CommandError
from stocks.models import Stock, KHistory

import csv

class Command(BaseCommand):
    help = '导入指数的PE-TTM数据'
    
    def handle(self, *args, **options):
        
        my_stocks = Stock.objects.all()
        for s in my_stocks:   
            with open('../pe_data/%s.csv' % s.code)as f:
                f_csv = csv.reader(f)
                i = 0
                row_count = sum(1 for row in f_csv)
                print('../pe_data/%s.csv' % s.code, row_count)
                
                f.seek(0) # back to beginning again
                for row in f_csv:
                    if i > 0 and len(row) > 0 and i < (row_count-2): # skip last 2 lines
                        print(row[0], row[4])
                        khs = KHistory.objects.filter(stock__code=s.code, date=row[0])
                        for k in khs:
                            k.peTTM = str(row[4])
                            k.save()
                    i += 1 # skip first line which is header