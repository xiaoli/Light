# Generated by Django 3.2.4 on 2021-07-21 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0006_auto_20210628_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='code',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='证券代码'),
        ),
    ]
