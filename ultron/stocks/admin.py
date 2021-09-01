from django.contrib import admin

from . import models

class StockAdmin(admin.ModelAdmin):
    search_fields = ['code', 'code_name']
    list_display = ('id', 'code', 'code_name', 'get_ipo_date', 'out_date', 'get_ipo_type', 'get_ipo_status')
    
    def get_ipo_type(self, obj):
        return obj.get_ipo_type_display()
    get_ipo_type.short_description = '证券类型'
    
    def get_ipo_status(self, obj):
        return obj.get_ipo_status_display()
    get_ipo_status.short_description = '上市状态'
    
    def get_ipo_date(self, obj):
        return obj.ipo_date.strftime("%Y-%m-%d")
    get_ipo_date.admin_order_field = 'ipo_date'
    get_ipo_date.short_description = '上市日期'

class KHistoryAdmin(admin.ModelAdmin):
    #list_display = ('id', 'get_stock', 'get_date', 'open_price', 'high_price', 'low_price', 'close_price', 'preclose_price', 
    #                'volume', 'amount', 'adjust_flag', 'turn', 'trades_tatus', 'pctChg', 'peTTM', 'psTTM', 'pcfNcfTTM',
    #                'pbMRQ', 'is_st')
                    
    list_display = ('id', 'get_stock', 'get_date', 'open_price', 'high_price', 'low_price', 'close_price',
                    'volume', 'amount', 'peTTM', 'maxPE', 'minPE')
    def get_stock(self, obj):
        return obj.stock.code_name
    get_stock.short_description = '证券名称'
    
    def get_date(self, obj):
        return obj.date.strftime("%Y-%m-%d")
    get_date.admin_order_field = 'date'
    get_date.short_description = '交易所行情日期'
    
class StrategyAdmin(admin.ModelAdmin):
    autocomplete_fields = ['stocks']
    list_display = ('id', 'name', 'get_s_type_display', 'get_available_display', 'top_limit', 'bottom_limit', 'status', 'created_date', 'updated_date', 'calculated_date')

class RuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'strategy', 'name', 'get_operation_display', 'limit', 'holding', 'get_available_display', 'priority', 'created_date', 'updated_date')

admin.site.register(models.Stock, StockAdmin)
admin.site.register(models.KHistory, KHistoryAdmin)
admin.site.register(models.Strategy, StrategyAdmin)
admin.site.register(models.Rule, RuleAdmin)