# Generated by Django 2.0.1 on 2018-01-31 14:54

from django.db import migrations, models
import django.db.models.deletion


def forward_func(apps, schema_editor):
    # Add default sources
    Source = apps.get_model("core", "Source")

    Source(id=0, name="Zkillboard (default)").save()
    Source(id=1, name="Zkill Redisq").save()
    Source(id=2, name="Zkill Historical API").save()
    Source(id=3, name="ESI").save()
    Source(id=4, name="CREST").save()
    

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20180129_1618'),
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.IntegerField(primary_key=True)),
                ('name', models.CharField(db_index=True, max_length=32)),
            ],
        ),
        migrations.RunPython(
            forward_func
        ),
        migrations.AddField(
            model_name='killmail',
            name='source',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='kills', to='core.Source'),
        ),
    ]
