from django.shortcuts import render
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Max, Min
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
import datetime
import requests

from .models import Stock, KHistory
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
    print(sid)
    
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