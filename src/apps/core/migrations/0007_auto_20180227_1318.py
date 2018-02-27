# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-27 13:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20180221_0718'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enrollwaregroup',
            name='synced',
        ),
        migrations.AddField(
            model_name='enrollwaregroup',
            name='status',
            field=models.CharField(choices=[('unsynced', 'Unsynced'), ('synced', 'Synced'), ('in_progress', 'In progress'), ('error', 'Error')], default='unsynced', max_length=12, verbose_name='status'),
        ),
    ]
