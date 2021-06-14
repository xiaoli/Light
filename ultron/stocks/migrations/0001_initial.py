# Generated by Django 3.2.4 on 2021-06-14 09:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=255, null=True, verbose_name='证券代码')),
                ('code_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='证券名称')),
                ('ipo_date', models.DateField(blank=True, max_length=10, null=True, verbose_name='上市日期')),
                ('out_date', models.DateField(blank=True, max_length=10, null=True, verbose_name='退市日期')),
                ('ipo_type', models.CharField(choices=[(1, '股票'), (2, '指数'), (3, '其它')], default=1, max_length=2, verbose_name='证券类型')),
                ('ipo_status', models.CharField(choices=[(1, '上市'), (0, '退市')], default=1, max_length=2, verbose_name='上市状态')),
            ],
            options={
                'verbose_name': '证券',
                'verbose_name_plural': '所有证券',
            },
        ),
        migrations.CreateModel(
            name='KHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='交易所行情日期')),
                ('open_price', models.CharField(blank=True, max_length=255, null=True, verbose_name='今开盘价格')),
                ('high_price', models.CharField(blank=True, max_length=255, null=True, verbose_name='最高价')),
                ('low_price', models.CharField(blank=True, max_length=255, null=True, verbose_name='最低价')),
                ('close_price', models.CharField(blank=True, max_length=255, null=True, verbose_name='今收盘价')),
                ('preclose_price', models.CharField(blank=True, max_length=255, null=True, verbose_name='昨日收盘价')),
                ('volume', models.CharField(blank=True, max_length=255, null=True, verbose_name='成交数量')),
                ('amount', models.CharField(blank=True, max_length=255, null=True, verbose_name='成交金额')),
                ('adjust_flag', models.CharField(choices=[(1, '后复权'), (2, '前复权'), (3, '不复权')], default=1, max_length=2, verbose_name='复权状态')),
                ('turn', models.CharField(blank=True, max_length=255, null=True, verbose_name='换手率 %')),
                ('trades_tatus', models.CharField(choices=[(1, '正常交易'), (0, '停牌')], default=1, max_length=2, verbose_name='交易状态')),
                ('pctChg', models.CharField(blank=True, max_length=255, null=True, verbose_name='涨跌幅（百分比）')),
                ('peTTM', models.CharField(blank=True, max_length=255, null=True, verbose_name='滚动市盈率')),
                ('psTTM', models.CharField(blank=True, max_length=255, null=True, verbose_name='滚动市销率')),
                ('pcfNcfTTM', models.CharField(blank=True, max_length=255, null=True, verbose_name='滚动市现率')),
                ('pbMRQ', models.CharField(blank=True, max_length=255, null=True, verbose_name='市净率')),
                ('is_st', models.CharField(choices=[(1, '是'), (0, '否')], default=0, max_length=2, verbose_name='复权状态')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.stock')),
            ],
            options={
                'verbose_name': 'K线数据',
                'verbose_name_plural': '所有K线数据',
            },
        ),
    ]
