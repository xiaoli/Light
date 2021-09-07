# Generated by Django 3.2.4 on 2021-09-07 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0011_auto_20210901_0242'),
    ]

    operations = [
        migrations.AddField(
            model_name='khistory',
            name='avgMaxPE',
            field=models.DecimalField(decimal_places=10, max_digits=19, null=True, verbose_name='近十年前30%最高平均市盈率'),
        ),
        migrations.AddField(
            model_name='khistory',
            name='avgMinPE',
            field=models.DecimalField(decimal_places=10, max_digits=19, null=True, verbose_name='近十年后30%最低平均市盈率'),
        ),
        migrations.AlterField(
            model_name='rule',
            name='limit',
            field=models.SmallIntegerField(default=1, verbose_name='高低估区间的档位，PE限值，单位%'),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='bottom_limit',
            field=models.SmallIntegerField(default=1, verbose_name='考察范围：低估下限值，单位%'),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='top_limit',
            field=models.SmallIntegerField(default=1, verbose_name='考察范围：高估上限值，单位%'),
        ),
    ]
