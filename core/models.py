from django.db import models

from sde.models import Type, System


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
    alliance = models.ForeignKey(Alliance, related_name="corporations", null=True, default=None, on_delete=models.SET_NULL)
    is_closed = models.BooleanField(default=False)

    founded = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class Character(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=64, db_index=True)
    birthday = models.DateTimeField()

    corporation = models.ForeignKey(Corporation, related_name="characters", on_delete=models.CASCADE)


# Instance of a killmail
class Killmail(models.Model):
    id = models.BigIntegerField(primary_key=True)

    # Victim
    character = models.ForeignKey(Character, related_name="losses", null=True, default=None, on_delete=models.SET_NULL)
    corporation = models.ForeignKey(Corporation, related_name="losses", null=True, default=None, on_delete=models.SET_NULL)
    alliance = models.ForeignKey(Alliance, null=True, related_name="losses", default=None, on_delete=models.SET_NULL)

    # Meta
    ship = models.ForeignKey(Type, related_name="attackers_ship", null=True, default=None, on_delete=models.CASCADE)
    weapon = models.ForeignKey(Type, null=True, related_name="attackers_weapon", default=None, on_delete=models.CASCADE)

    system = models.ForeignKey(System, related_name="kills", on_delete=models.CASCADE)
    date = models.DateTimeField(db_index=True)
    added = models.DateTimeField(auto_now_add=True)

    value = models.DecimalField(max_digits=20, decimal_places=2, db_index=True)


# Instance of an attacker on a killmail
class Attacker(models.Model):
    kill = models.ForeignKey(Killmail, related_name="attackers", on_delete=models.CASCADE)

    character = models.ForeignKey(Character, related_name="kills", null=True, default=None, on_delete=models.SET_NULL)
    corporation = models.ForeignKey(Corporation, related_name="kills", null=True, default=None, on_delete=models.SET_NULL)
    alliance = models.ForeignKey(Alliance, null=True, related_name="kills", default=None, on_delete=models.SET_NULL)

    ship = models.ForeignKey(Type,related_name="victim_ship", null=True, default=None, on_delete=models.CASCADE)
    weapon = models.ForeignKey(Type, null=True, related_name="victim_weapon", default=None, on_delete=models.CASCADE)

    damage = models.IntegerField(db_index=True)