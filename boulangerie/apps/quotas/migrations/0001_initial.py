# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-18 12:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Quota',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.SlugField()),
                ('value', models.DecimalField(decimal_places=5, max_digits=15)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('owner', models.SlugField()),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='quota',
            unique_together=set([('key', 'owner')]),
        ),
    ]
