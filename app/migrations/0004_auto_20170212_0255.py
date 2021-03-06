# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-12 02:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_link_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='contextualcandidates',
            name='text',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='contextualcandidates',
            name='wordCandidates',
            field=models.ManyToManyField(related_name='contexts', to='app.wordCandidate'),
        ),
        migrations.AlterField(
            model_name='link',
            name='structuralCandidates',
            field=models.ManyToManyField(related_name='struct', to='app.structuralCandidates'),
        ),
        migrations.AlterField(
            model_name='structuralcandidates',
            name='contextualCandidates',
            field=models.ManyToManyField(related_name='struct', to='app.contextualCandidates'),
        ),
    ]
