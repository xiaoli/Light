from django.db import models

class Stock(models.Model):
    TYPE_CHOICES = (
        (1, '股票'),
        (2, '指数'),
        (3, '其它')
    )
    
    STATUS_CHOICES = (
        (1, '上市'),
        (0, '退市')
    )
    
    code = models.CharField(max_length=255, blank=True, null=True, verbose_name="证券代码")
    code_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="证券名称")
    ipo_date = models.DateField(max_length=10, blank=True, null=True, verbose_name="上市日期")
    out_date = models.DateField(max_length=10, blank=True, null=True, verbose_name="退市日期")
    ipo_type = models.SmallIntegerField(
        choices=TYPE_CHOICES,
        default=1,
        verbose_name="证券类型"
    )
    ipo_status = models.SmallIntegerField(
        choices=STATUS_CHOICES,
        default=1,
        verbose_name="上市状态"
    )
    
    def __str__(self):
            return '%s' % (self.code_name)
    
    class Meta:
        verbose_name = "证券"
        verbose_name_plural = "所有证券"
        
class KHistory(models.Model):
    FLAG_CHOICES = (
        (1, '后复权'),
        (2, '前复权'),
        (3, '不复权')
    )
    
    STATUS_CHOICES = (
        (1, '正常交易'),
        (0, '停牌')
    )
    ST_CHOICES = (
        (1, '是'),
        (0, '否')
    )
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, verbose_name='证券名称')
    date = models.DateField(verbose_name="交易所行情日期")
    open_price = models.CharField(max_length=255, blank=True, null=True, verbose_name="今开盘价格")
    high_price = models.CharField(max_length=255, blank=True, null=True, verbose_name="最高价")
    low_price = models.CharField(max_length=255, blank=True, null=True, verbose_name="最低价")
    close_price = models.CharField(max_length=255, blank=True, null=True, verbose_name="今收盘价")
    preclose_price = models.CharField(max_length=255, blank=True, null=True, verbose_name="昨日收盘价")
    volume = models.CharField(max_length=255, blank=True, null=True, verbose_name="成交数量")
    amount = models.CharField(max_length=255, blank=True, null=True, verbose_name="成交金额")
    adjust_flag = models.SmallIntegerField(
        choices=FLAG_CHOICES,
        default=1,
        verbose_name="复权状态"
    )
    turn = models.CharField(max_length=255, blank=True, null=True, verbose_name="换手率 %")
    trades_tatus = models.SmallIntegerField(
        choices=STATUS_CHOICES,
        default=1,
        verbose_name="交易状态"
    )
    pctChg = models.CharField(max_length=255, blank=True, null=True, verbose_name="涨跌幅（百分比）")
    peTTM = models.CharField(max_length=255, blank=True, null=True, verbose_name="滚动市盈率")
    avgPE = models.CharField(max_length=255, blank=True, null=True, verbose_name="近十年滚动市盈率")
    psTTM = models.CharField(max_length=255, blank=True, null=True, verbose_name="滚动市销率")
    pcfNcfTTM = models.CharField(max_length=255, blank=True, null=True, verbose_name="滚动市现率")
    pbMRQ = models.CharField(max_length=255, blank=True, null=True, verbose_name="市净率")
    is_st = models.SmallIntegerField(
        choices=ST_CHOICES,
        default=0,
        verbose_name="是否ST"
    )
    
    class Meta:
        verbose_name = "K线数据"
        verbose_name_plural = "所有K线数据"