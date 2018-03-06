# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-03-02 13:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0007_auto_20180227_1318'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ahacredentials',
            options={'verbose_name': 'aha credential', 'verbose_name_plural': 'aha credentials'},
        ),
        migrations.AlterModelOptions(
            name='enrollwarecredentials',
            options={'verbose_name': 'enroll credential', 'verbose_name_plural': 'enroll credentials'},
        ),
        migrations.AddField(
            model_name='ahafield',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='aha_fields', to=settings.AUTH_USER_MODEL, verbose_name='user'),
            preserve_default=False,
        ),
    ]