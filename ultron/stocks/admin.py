from django.contrib import admin

from . import models

class StockAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'code_name', 'ipo_date', 'out_date', 'ipo_type', 'ipo_status')

class KHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'stock', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'preclose_price', 
                    'volume', 'amount', 'adjust_flag', 'turn', 'trades_tatus', 'pctChg', 'peTTM', 'psTTM', 'pcfNcfTTM',
                    'pbMRQ', 'is_st')

admin.site.register(models.Stock, StockAdmin)
admin.site.register(models.KHistory, KHistoryAdmin)
