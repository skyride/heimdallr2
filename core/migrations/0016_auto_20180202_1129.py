# Generated by Django 2.0.1 on 2018-02-02 11:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_migrate_victim_to_involved'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='killmail',
            name='alliance',
        ),
        migrations.RemoveField(
            model_name='killmail',
            name='character',
        ),
        migrations.RemoveField(
            model_name='killmail',
            name='corporation',
        ),
    ]
