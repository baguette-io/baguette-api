# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-17 20:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20170517_0312'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='id',
        ),
        migrations.AlterField(
            model_name='account',
            name='username',
            field=models.SlugField(primary_key=True, serialize=False, unique=True),
        ),
    ]
