# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-02-25 16:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_auto_20190225_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterUniqueTogether(
            name='resource',
            unique_together=set([('name', 'project', 'request_type')]),
        ),
    ]
