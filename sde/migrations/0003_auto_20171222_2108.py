# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-22 21:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sde', '0002_auto_20171222_2104'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='fittableNonSingleton',
            new_name='fittable_non_singleton',
        ),
    ]
