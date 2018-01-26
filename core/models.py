import requests
from django.db import models
from django.conf import settings
from django.utils.dateparse import parse_datetime

from sde.models import Type, System


class Alliance(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=64, db_index=True)
    ticker = models.CharField(max_length=5, db_index=True)

    founded = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s:%s" % (
            self.id,
            self.name
        )

    @staticmethod
    def get_or_create(id):
        try:
            return Alliance.objects.get(id=id)
        except models.ObjectDoesNotExist:
            r = requests.get(
                "%s/v3/alliances/%s/" % (
                    settings.ESI_BASE,
                    id
                )
            )

            if r.status_code == 200:
                r = r.json()
                o = Alliance(
                    id=id,
                    name=r['name'],
                    ticker=r['ticker'],
                    founded=parse_datetime(r['date_founded'])
                )
                o.save()
                return o


class Corporation(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=64, db_index=True)
    ticker = models.CharField(max_length=5, db_index=True)
    alliance = models.ForeignKey(Alliance, related_name="corporations", null=True, default=None, on_delete=models.SET_NULL)
    is_closed = models.BooleanField(default=False, db_index=True)

    founded = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s:%s" % (
            self.id,
            self.name
        )

    @staticmethod
    def get_or_create(id):
        try:
            return Corporation.objects.get(id=id)
        except models.ObjectDoesNotExist:
            r = requests.get(
                "%s/v4/corporations/%s/" % (
                    settings.ESI_BASE,
                    id
                )
            )

            if r.status_code == 200:
                r = r.json()
                o = Corporation(
                    id=id,
                    name=r['name'],
                    ticker=r['ticker'],
                    founded=parse_datetime(r['date_founded'])
                )

                if "alliance_id" in r:
                    o.alliance = Alliance.get_or_create(r['alliance_id'])
                if r['member_count'] == 0:
                    o.is_closed = True

                o.save()
                return o


class Character(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=64, db_index=True)
    birthday = models.DateTimeField()
    corporation = models.ForeignKey(Corporation, related_name="characters", on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s:%s" % (
            self.id,
            self.name
        )

    @staticmethod
    def get_or_create(id):
        try:
            return Character.objects.get(id=id)
        except models.ObjectDoesNotExist:
            r = requests.get(
                "%s/v4/characters/%s/" % (
                    settings.ESI_BASE,
                    id
                )
            )

            if r.status_code == 200:
                r = r.json()
                o = Character(
                    id=id,
                    name=r['name'],
                    birthday=parse_datetime(r['birthday']),
                    corporation=Corporation.get_or_create(r['corporation_id'])
                )

                o.save()
                return o


# Instance of a killmail
class Killmail(models.Model):
    id = models.BigIntegerField(primary_key=True)
    date = models.DateTimeField(db_index=True)
    system = models.ForeignKey(System, related_name="kills", on_delete=models.CASCADE)

    # Victim
    character = models.ForeignKey(Character, related_name="losses", null=True, default=None, on_delete=models.SET_NULL)
    corporation = models.ForeignKey(Corporation, related_name="losses", null=True, default=None, on_delete=models.SET_NULL)
    alliance = models.ForeignKey(Alliance, null=True, related_name="losses", default=None, on_delete=models.SET_NULL)

    # Meta
    ship = models.ForeignKey(Type, related_name="attackers_ship", null=True, default=None, on_delete=models.CASCADE)

    value = models.DecimalField(max_digits=20, decimal_places=2, db_index=True)
    damage = models.IntegerField(db_index=True)

    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()

    added = models.DateTimeField(auto_now_add=True)


# Instance of an attacker on a killmail
class Attacker(models.Model):
    kill = models.ForeignKey(Killmail, related_name="attackers", on_delete=models.CASCADE)

    character = models.ForeignKey(Character, related_name="kills", null=True, default=None, on_delete=models.SET_NULL)
    corporation = models.ForeignKey(Corporation, related_name="kills", null=True, default=None, on_delete=models.SET_NULL)
    alliance = models.ForeignKey(Alliance, null=True, related_name="kills", default=None, on_delete=models.SET_NULL)

    ship = models.ForeignKey(Type,related_name="victim_ship", null=True, default=None, on_delete=models.CASCADE)
    weapon = models.ForeignKey(Type, null=True, related_name="victim_weapon", default=None, on_delete=models.CASCADE)

    damage = models.IntegerField(db_index=True)