# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-16 12:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20180516_1257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollclasstime',
            name='group_id',
            field=models.CharField(default='', max_length=128, verbose_name='group id'),
        ),
        migrations.AlterField(
            model_name='enrollwaregroup',
            name='group_id',
            field=models.CharField(default='', max_length=128, verbose_name='group id'),
        ),
    ]