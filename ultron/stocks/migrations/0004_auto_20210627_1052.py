# Generated by Django 3.2.4 on 2021-06-27 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0003_auto_20210627_0309'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='khistory',
            name='avgPE',
        ),
        migrations.AddField(
            model_name='khistory',
            name='maxPE',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='近十年最高市盈率'),
        ),
        migrations.AddField(
            model_name='khistory',
            name='minPE',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='近十年最低市盈率'),
        ),
    ]