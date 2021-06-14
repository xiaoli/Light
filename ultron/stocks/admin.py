from django.contrib import admin

from . import models

class StockAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'code_name', 'ipo_date', 'out_date', 'get_ipo_type', 'get_ipo_status')
    
    def get_ipo_type(self, obj):
        return obj.get_ipo_type_display()
    get_ipo_type.short_description = '证券类型'
    
    def get_ipo_status(self, obj):
        return obj.get_ipo_status_display()
    get_ipo_status.short_description = '上市状态'

class KHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'stock', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'preclose_price', 
                    'volume', 'amount', 'adjust_flag', 'turn', 'trades_tatus', 'pctChg', 'peTTM', 'psTTM', 'pcfNcfTTM',
                    'pbMRQ', 'is_st')

admin.site.register(models.Stock, StockAdmin)
admin.site.register(models.KHistory, KHistoryAdmin)
