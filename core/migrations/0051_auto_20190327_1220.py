# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-03-27 12:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0050_auto_20190327_1216'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='resourceusergroup',
            unique_together=set([]),
        ),
    ]
