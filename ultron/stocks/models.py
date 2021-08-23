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
    
    code = models.CharField(max_length=255, unique=True, blank=True, null=True, verbose_name="证券代码")
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
    open_price = models.DecimalField(max_digits=19, decimal_places=10, null=True, verbose_name="今开盘价格")
    high_price = models.DecimalField(max_digits=19, decimal_places=10, null=True, verbose_name="最高价")
    low_price = models.DecimalField(max_digits=19, decimal_places=10, null=True, verbose_name="最低价")
    close_price = models.DecimalField(max_digits=19, decimal_places=10, null=True, verbose_name="今收盘价")
    preclose_price = models.DecimalField(max_digits=19, decimal_places=10, null=True, verbose_name="昨日收盘价")
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
    pctChg = models.DecimalField(max_digits=19, decimal_places=10, null=True, verbose_name="涨跌幅（百分比）")
    peTTM = models.DecimalField(max_digits=19, decimal_places=10, null=True, verbose_name="滚动市盈率")
    maxPE = models.DecimalField(max_digits=19, decimal_places=10, null=True, verbose_name="近十年最高市盈率")
    minPE = models.DecimalField(max_digits=19, decimal_places=10, null=True, verbose_name="近十年最低市盈率")
    avgPE = models.DecimalField(max_digits=19, decimal_places=10, null=True, verbose_name="近十年平均市盈率")
    psTTM = models.DecimalField(max_digits=19, decimal_places=10, null=True, verbose_name="滚动市销率")
    pcfNcfTTM = models.DecimalField(max_digits=19, decimal_places=10, null=True, verbose_name="滚动市现率")
    pbMRQ = models.DecimalField(max_digits=19, decimal_places=10, null=True, verbose_name="市净率")
    is_st = models.SmallIntegerField(
        choices=ST_CHOICES,
        default=0,
        verbose_name="是否ST"
    )
    
    class Meta:
        verbose_name = "K线数据"
        verbose_name_plural = "所有K线数据"
        
class Strategy(models.Model):
    
    STATUS_CHOICES = (
        (2, '运算完毕'),
        (1, '运算中'),
        (0, '新创建')
    )
    
    AVAILABLE_CHOICES = (
        (1, '生效中'),
        (0, '无效')
    )
    
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="策略名称")
    available = models.SmallIntegerField(
        choices=AVAILABLE_CHOICES,
        default=1,
        verbose_name="是否生效"
    )
    top_limit = models.SmallIntegerField(default=1, verbose_name="高估区间，PE Range 上限值，单位%")
    bottom_limit = models.SmallIntegerField(default=1, verbose_name="低估区间，PE Range 下限值，单位%")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    calculated_date = models.DateTimeField(blank=True, null=True, verbose_name="运算时间")
    status = models.SmallIntegerField(
        choices=STATUS_CHOICES,
        default=0,
        verbose_name="状态"
    )
    
    def __str__(self):
            return '%s' % (self.name)
    
    class Meta:
        verbose_name = "策略"
        verbose_name_plural = "所有策略"
        
class Rule(models.Model):
    
    OPERATION_CHOICES = (
        (2, '高估操作（卖出）'),
        (1, '低估操作（买进）')
    )
    
    STATUS_CHOICES = (
        (2, '运算完毕'),
        (1, '运算中'),
        (0, '新创建')
    )
    
    AVAILABLE_CHOICES = (
        (1, '生效中'),
        (0, '无效')
    )
    
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE, verbose_name='策略名称')
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="规则名称")
    operation = models.SmallIntegerField(
        choices=OPERATION_CHOICES,
        default=1,
        verbose_name="高估 or 低估"
    )
    limit = models.SmallIntegerField(default=1, verbose_name="高低估区间，PE Range 上限值，单位%")
    holding = models.SmallIntegerField(default=1, verbose_name="股票持仓比例，单位%")
    available = models.SmallIntegerField(
        choices=AVAILABLE_CHOICES,
        default=1,
        verbose_name="是否生效"
    )
    priority = models.SmallIntegerField(default=1, verbose_name="优先级")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    def __str__(self):
            return '%s' % (self.name)
    
    class Meta:
        verbose_name = "规则"
        verbose_name_plural = "所有规则"