# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-02-06 16:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20190206_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endpointdatasourcefilter',
            name='column_parameter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.EndpointDataSourceColumn'),
        ),
        migrations.AlterField(
            model_name='endpointdatasourcefilter',
            name='request_parameter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.EndpointParameter'),
        ),
        migrations.AlterField(
            model_name='endpointdatasourcefilter',
            name='type',
            field=models.CharField(choices=[('REQUEST', 'Parameter sent in request, either GET or POST'), ('COLUMN', 'Parameter from another column.')], max_length=6),
        ),
    ]
