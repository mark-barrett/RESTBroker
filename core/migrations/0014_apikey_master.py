# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-01-30 10:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20190129_1648'),
    ]

    operations = [
        migrations.AddField(
            model_name='apikey',
            name='master',
            field=models.BooleanField(default=True),
        ),
    ]
