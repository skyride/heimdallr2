import ujson

from django.utils.dateparse import parse_datetime

from heimdallr.celery import app
from core.models import Killmail, Attacker, Item, Character, Corporation, Alliance
from sde.models import System, Type


@app.task(name="parse_redisq")
def parse_redisq(json):
    package = ujson.loads(json)['package']
    killmail = package['killmail']
    victim = killmail['victim']
    zkb = package['zkb']

    # Check the KM doesn't already exist
    if Killmail.objects.filter(id=package['killID']).count() > 0:
        print("Kill ID %s already exists" % package['killID'])
        return

    # Populate killmail
    km = Killmail(
        id=package['killID'],
        date=parse_datetime(killmail['killmail_time']),
        system_id=killmail['solar_system_id'],
        ship_id=victim['ship_type_id'],
        value=zkb['totalValue'],
        damage=victim['damage_taken']
    )

    if "position" in victim['position']:
        km.x = victim['position']['x']
        km.y = victim['position']['y']
        km.z = victim['position']['z']

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

        if "final_blow" in attacker:
            a.final_blow = attacker['final_blow']
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
        a.save()
        attackers.append(a)

    # Populate Items
    for item in victim['items']:
        i = Item(
            kill=km,
            type_id=item['item_type_id'],
            singleton=item['singleton'],
            flag=item['flag']
        )

        if "quantity_dropped" in item:
            i.quantity = item['quantity_dropped']
        if "quantity_destroyed" in item:
            i.quantity = item['quantity_destroyed']
        i.save()

    print(
        "Added Kill ID %s with %s attackers" % (
            km.id,
            len(attackers)
        )
    )


@app.task(name="parse_zkill_api")
def parse_zkill_api(json):
    package = ujson.loads(json)
    victim = package['victim']
    position = victim['position']
    zkb = package['zkb']

    # Check the KM doesn't already exist
    if Killmail.objects.filter(id=package['killmail_id']).count() > 0:
        print("Kill ID %s already exists" % package['killmail_id'])
        return

    # Populate killmail
    km = Killmail(
        id=package['killmail_id'],
        date=parse_datetime(package['killmail_time']),
        system_id=package['solar_system_id'],
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
    for attacker in package['attackers']:
        a = Attacker(
            kill=km,
            damage=attacker['damage_done']
        )

        if "final_blow" in attacker:
            a.final_blow = attacker['final_blow']
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
        a.save()
        attackers.append(a)

    # Populate Items
    items = []
    for item in victim['items']:
        i = Item(
            kill=km,
            type_id=item['item_type_id'],
            singleton=item['singleton'],
            flag=item['flag']
        )

        if "quantity_dropped" in item:
            i.quantity = item['quantity_dropped']
        if "quantity_destroyed" in item:
            i.quantity = item['quantity_destroyed']
        i.save()
        items.append(i)

    print(
        "Added Kill ID %s with %s attackers" % (
            km.id,
            len(attackers)
        )
    )

    