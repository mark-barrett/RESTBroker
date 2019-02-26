# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-02-26 14:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_blockedip_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blockedip',
            name='type',
        ),
        migrations.AddField(
            model_name='resourcedatabind',
            name='type',
            field=models.CharField(choices=[('Integer', 'Integer: Positive or Negative whole number'), ('Decimal', 'Decimal: Positive or Negative number with decimal'), ('String', 'String: Text'), ('Boolean', 'Boolean: True or False')], default=1, max_length=32),
            preserve_default=False,
        ),
    ]