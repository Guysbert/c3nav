# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-24 18:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0032_auto_20161223_2225'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationgroup',
            name='can_describe',
            field=models.BooleanField(default=True, verbose_name='can be used to describe a position'),
        ),
        migrations.AlterField(
            model_name='locationgroup',
            name='compiled_room',
            field=models.BooleanField(default=False, verbose_name='is a compiled room'),
        ),
    ]