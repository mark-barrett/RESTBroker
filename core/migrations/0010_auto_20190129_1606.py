# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-01-29 16:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_project_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(default='No description', null=True),
        ),
    ]
