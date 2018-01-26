# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-30 14:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sde', '0011_auto_20171229_1529'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttributeCategory',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='AttributeType',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=400)),
                ('description', models.CharField(max_length=1000, null=True)),
                ('iconID', models.IntegerField(null=True)),
                ('default_value', models.IntegerField(null=True)),
                ('published', models.BooleanField(db_index=True)),
                ('display_name', models.CharField(max_length=150, null=True)),
                ('unitID', models.IntegerField(null=True)),
                ('stackable', models.BooleanField()),
                ('high_is_good', models.BooleanField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sde.AttributeCategory')),
            ],
        ),
        migrations.CreateModel(
            name='TypeAttribute',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sde.AttributeType')),
            ],
        ),
    ]
