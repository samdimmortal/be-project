# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-16 15:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20170213_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='webresource',
            name='urls',
            field=models.TextField(blank=True),
        ),
    ]
