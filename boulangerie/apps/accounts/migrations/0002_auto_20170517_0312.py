# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-17 03:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='username',
            field=models.SlugField(unique=True),
        ),
    ]