# Generated by Django 2.0.1 on 2018-02-02 11:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_rename_attacker_to_involved'),
    ]

    operations = [
        migrations.AddField(
            model_name='involved',
            name='attacker',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='involved',
            name='ship',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='involved_ship', to='sde.Type'),
        ),
        migrations.AlterField(
            model_name='involved',
            name='weapon',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='involved_weapon', to='sde.Type'),
        ),
        migrations.AlterField(
            model_name='killmail',
            name='ship',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='losses_ship', to='sde.Type'),
        ),
    ]
