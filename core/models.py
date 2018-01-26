from django.db import models


class Alliance(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=64, db_index=True)
    ticker = models.CharField(max_length=5, db_index=True)
    is_closed = models.BooleanField(default=False)

    founded = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class Corporation(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=64, db_index=True)
    ticker = models.CharField(max_length=5, db_index=True)
    alliance = models.ForeignKey(Alliance, null=True, default=None, on_delete=models.SET_NULL)
    is_closed = models.BooleanField(default=False)

    founded = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class Character(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=64, db_index=True)
    birthday = models.DateTimeField()