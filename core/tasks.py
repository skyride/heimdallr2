import ujson

from django.utils.dateparse import parse_datetime

from core.models import Killmail, Attacker, Character, Corporation, Alliance
from sde.models import System, Type


def parse_redisq(json):
    package = ujson.loads(json)['package']
    killmail = package['killmail']
    victim = killmail['victim']
    items = victim['items']
    position = victim['position']
    zkb = package['zkb']

    # Check the KM doesn't already exist
    if Killmail.objects.filter(id=package['killID']).count() > 0:
        return

    # Populate killmail
    km = Killmail(
        id=package['killID'],
        date=parse_datetime(killmail['killmail_time']),
        system_id=killmail['solar_system_id'],
        ship_id=victim['ship_type_id'],
        value=zkb['totalValue'],
        damage=victim['damage_taken'],
        x=position['x'],
        y=position['y'],
        z=position['z']
    )

    if "character_id" in victim:
        km.character = Character.get_or_create(victim['character_id'])
    if "corporation_id" in victim:
        km.corporation = Corporation.get_or_create(victim['corporation_id'])
    if "alliance_id" in victim:
        km.alliance = Alliance.get_or_create(victim['alliance_id'])
    km.save()

    # Populate attackers
    attackers = []
    for attacker in killmail['attackers']:
        a = Attacker(
            kill=km,
            damage=attacker['damage_done']
        )

        if "character_id" in attacker:
            a.character = Character.get_or_create(attacker['character_id'])
        if "corporation_id" in attacker:
            a.corporation = Corporation.get_or_create(attacker['corporation_id'])
        if "alliance_id" in attacker:
            a.alliance = Alliance.get_or_create(attacker['alliance_id'])

        if "ship_type_id" in attacker:
            a.ship_id = attacker['ship_type_id']
        if "weapon_type_id" in attacker:
            a.weapon_id = attacker['weapon_type_id']

        attackers.append(a)
    Attacker.objects.bulk_create(attackers)

    