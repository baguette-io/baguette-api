# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-13 08:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vpcs', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vpc',
            options={'ordering': ('date_created',)},
        ),
    ]
