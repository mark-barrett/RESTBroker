# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-02-06 16:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20190206_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='endpointdatasourcefilter',
            name='endpoint',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.Endpoint'),
            preserve_default=False,
        ),
    ]
