# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-11 23:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='release',
            options={'ordering': ['repo__product_name', '-time_created']},
        ),
    ]
