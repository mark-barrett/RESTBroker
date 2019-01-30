# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-01-29 16:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20190129_1630'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Project')),
            ],
            options={
                'verbose_name_plural': 'API Keys',
            },
        ),
    ]