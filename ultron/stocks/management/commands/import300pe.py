# -*- coding:utf-8 -*-
from datetime import date
import json
import requests

from django.core.management.base import BaseCommand, CommandError
from stocks.models import Stock, KHistory

import csv

class Command(BaseCommand):
    help = '导入沪深300指数的PE-TTM数据'
    
    def handle(self, *args, **options):
        
        with open('300.csv')as f:
            f_csv = csv.reader(f)
            i = 0
            for row in f_csv:
                if i > 0 and len(row) > 0:
                    print(row[0], row[4])
                    khs = KHistory.objects.filter(stock__code="sh.000300", date=row[0])
                    for k in khs:
                        k.peTTM = str(row[4])
                        k.save()
                i += 1