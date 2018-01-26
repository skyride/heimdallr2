# Generated by Django 2.0.1 on 2018-01-26 11:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alliance',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=64)),
                ('ticker', models.CharField(db_index=True, max_length=5)),
                ('is_closed', models.BooleanField(default=False)),
                ('founded', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=64)),
                ('birthday', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Corporation',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=64)),
                ('ticker', models.CharField(db_index=True, max_length=5)),
                ('is_closed', models.BooleanField(default=False)),
                ('founded', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('alliance', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Alliance')),
            ],
        ),
    ]
