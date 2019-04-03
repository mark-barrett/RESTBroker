# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-04-03 14:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0053_resourceusergroup'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResourceTextSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Resource')),
            ],
            options={
                'verbose_name_plural': 'Resource Text Sources',
            },
        ),
    ]
