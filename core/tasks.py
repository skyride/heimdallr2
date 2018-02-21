from datetime import datetime
from time import sleep

import ujson
import requests

from django.db import transaction
from django.db.models import ExpressionWrapper, Sum, F, FloatField
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware

from heimdallr.celery import app
from core.helpers import parse_crest_date
from core.models import Killmail, Involved, Item, Character, Corporation, Alliance
from sde.models import System, Type



@app.task(name="fetch_character_kills", queue="control")
def fetch_character_kills(id):
    char = Character.get_or_create(id)
    url = "https://zkillboard.com/api/characterID/%s/page/%s/"
    _fetch_kills(char, url)


@app.task(name="fetch_corporation_kills", queue="control")
def fetch_corporation_kills(id):
    corp = Corporation.get_or_create(id)
    url = "https://zkillboard.com/api/corporationID/%s/page/%s/"
    _fetch_kills(corp, url)


@app.task(name="fetch_alliance_kills", queue="control")
def fetch_alliance_kills(id):
    alliance = Alliance.get_or_create(id)
    url = "https://zkillboard.com/api/allianceID/%s/page/%s/"
    _fetch_kills(alliance, url)


def _fetch_kills(obj, url):
    limit = make_aware(datetime(2015, 10, 1))
    
    i = 1
    count = 0
    pages = 0
    while True:
        rs = requests.get(url % (obj.id, i))
        if rs.status_code == 200:
            rs = rs.json()

            if len(rs) > 0:
                pages = pages + 1

                for r in rs:
                    parse_zkill_api.delay(ujson.dumps(r))
                    count = count + 1
                
                if parse_datetime(rs[-1]['killmail_time']) < limit:
                    break
            else:
                break
        else:
            break

        i = i + 1

    print(
        "Fetched %s kills from %s pages for %s:%s" % (
            count,
            pages,
            obj.id,
            obj.name
        )
    )


@app.task(name="parse_redisq", queue="high")
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
        source_id=1,
        date=parse_datetime(killmail['killmail_time']),
        system_id=killmail['solar_system_id'],
        ship_id=victim['ship_type_id'],
        value=zkb['totalValue'],
        damage=victim['damage_taken'],
        attackers=len(killmail['attackers'])
    )

    if "position" in victim:
        km.x = victim['position']['x']
        km.y = victim['position']['y']
        km.z = victim['position']['z']

    db_victim = Involved(
        kill=km,
        attacker=False,
        ship_id=victim['ship_type_id'],
        damage=0
    )
    if "character_id" in victim:
        db_victim.character = Character.get_or_create(victim['character_id'])
    if "corporation_id" in victim:
        db_victim.corporation = Corporation.get_or_create(victim['corporation_id'])
    if "alliance_id" in victim:
        db_victim.alliance = Alliance.get_or_create(victim['alliance_id'])
    km.save()

    # Populate Involved
    attackers = [db_victim]
    for attacker in killmail['attackers']:
        a = Involved(
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
        #a.save()
        attackers.append(a)
    Involved.objects.bulk_create(attackers)

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
        #i.save()
        items.append(i)
    Item.objects.bulk_create(items)

    print(
        "Added Kill ID %s on %s with %s involved from Redisq" % (
            km.id,
            km.date.strftime("%d/%m/%Y %H:%M"),
            len(attackers)
        )
    )


@app.task(name="parse_zkill_api", queue="low")
def parse_zkill_api(json):
    package = ujson.loads(json)
    victim = package['victim']
    zkb = package['zkb']

    # Check the KM doesn't already exist
    if Killmail.objects.filter(id=package['killmail_id']).count() > 0:
        print("Kill ID %s already exists" % package['killmail_id'])
        return

    # Populate killmail
    km = Killmail(
        id=package['killmail_id'],
        source_id=2,
        date=parse_datetime(package['killmail_time']),
        system_id=package['solar_system_id'],
        ship_id=victim['ship_type_id'],
        value=zkb['totalValue'],
        damage=victim['damage_taken']
    )

    if "position" in victim:
        if "x" in victim['position']:
            km.x = victim['position']['x']
            km.y = victim['position']['y']
            km.z = victim['position']['z']

    db_victim = Involved(
        kill=km,
        attacker=False,
        ship_id=victim['ship_type_id'],
        damage=0
    )
    if "character_id" in victim:
        db_victim.character = Character.get_or_create(victim['character_id'])
    if "corporation_id" in victim:
        db_victim.corporation = Corporation.get_or_create(victim['corporation_id'])
    if "alliance_id" in victim:
        db_victim.alliance = Alliance.get_or_create(victim['alliance_id'])

    km.save()

    # Populate attackers
    attackers = [db_victim]
    for attacker in package['attackers']:
        a = Involved(
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
        #a.save()
        attackers.append(a)
    Involved.objects.bulk_create(attackers)

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
        #i.save()
        items.append(i)
    Item.objects.bulk_create(items)

    print(
        "Added Kill ID %s on %s with %s involved from zkill API" % (
            km.id,
            km.date.strftime("%d/%m/%Y %H:%M"),
            len(attackers)
        )
    )


@app.task(name="parse_esi", queue="low")
def parse_esi(json=None, keyhash=None, attempts=0, source_id=3):
    if json != None:
        package = ujson.loads(json)
        victim = package['victim']
        if Killmail.objects.filter(id=package['killmail_id']).count() > 0:
            print("Kill ID %s already exists" % package['killmail_id'])
            return
    else:
        if Killmail.objects.filter(id=keyhash[0]).count() > 0:
            print("Kill ID %s already exists" % keyhash[0])
            return


        package = requests.get("https://esi.tech.ccp.is/latest/killmails/%s/%s/" % (keyhash[0], keyhash[1]))
        if package.status_code != 200:
            if attempts < 5:
                sleep(1)
                return parse_esi(keyhash=keyhash, attempts=attempts+1)
            else:
                print("Error fetching kill ID %s from ESI" % keyhash[0])
                return None
        package = package.json()
        victim = package['victim']

    # Pre-load char/corp/alliance sets so we can fill the database
    chars = set()
    corps = set()
    alliances = set()

    if "character_id" in victim:
        chars.add(victim['character_id'])
    if "corporation_id" in victim:
        corps.add(victim['corporation_id'])
    if "alliance_id" in victim:
        alliances.add(victim['alliance_id'])

    for attacker in package['attackers']:
        if "character_id" in attacker:
            chars.add(attacker['character_id'])
        if "corporation_id" in attacker:
            corps.add(attacker['corporation_id'])
        if "alliance_id" in attacker:
            alliances.add(attacker['alliance_id'])

    # Now call get_or_create to preload them in the database
    for char in chars:
        Character.get_or_create(char)
    for corp in corps:
        Corporation.get_or_create(corp)
    for alliance in alliances:
        Alliance.get_or_create(alliance)

    # Populate killmail and data within transaction
    with transaction.atomic():
        km = Killmail(
            id=package['killmail_id'],
            source_id=source_id,
            date=parse_datetime(package['killmail_time']),
            system_id=package['solar_system_id'],
            ship_id=victim['ship_type_id'],
            value=0,
            damage=victim['damage_taken'],
            attackers=len(package['attackers'])
        )

        if "position" in victim:
            if "x" in victim['position']:
                km.x = victim['position']['x']
                km.y = victim['position']['y']
                km.z = victim['position']['z']

        db_victim = Involved(
            kill=km,
            attacker=False,
            ship_id=victim['ship_type_id'],
            damage=0
        )
        if "character_id" in victim:
            db_victim.character = Character.get_or_create(victim['character_id'])
        if "corporation_id" in victim:
            db_victim.corporation = Corporation.get_or_create(victim['corporation_id'])
        if "alliance_id" in victim:
            db_victim.alliance = Alliance.get_or_create(victim['alliance_id'])

        km.save()

        # Populate attackers
        attackers = [db_victim]
        for attacker in package['attackers']:
            a = Involved(
                kill=km,
                damage=attacker['damage_done']
            )

            if "final_blow" in attacker:
                a.final_blow = attacker['final_blow']
            if "character_id" in attacker:
                a.character_id = attacker['character_id']
            if "corporation_id" in attacker:
                a.corporation_id = attacker['corporation_id']
            if "alliance_id" in attacker:
                a.alliance_id = attacker['alliance_id']

            if "ship_type_id" in attacker:
                a.ship_id = attacker['ship_type_id']
            if "weapon_type_id" in attacker:
                a.weapon_id = attacker['weapon_type_id']
            #a.save()
            attackers.append(a)
        Involved.objects.bulk_create(attackers)

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
            #i.save()
            items.append(i)
        Item.objects.bulk_create(items)

        # Calculate the cost of the ship
        km.value = km.items.annotate(
            value=ExpressionWrapper(
                F('type__sell') * F('quantity'),
                output_field=FloatField()
            )
        ).aggregate(
            total_value=Sum('value')
        )['total_value'] or 0 + float(km.ship.sell)

    print(
        "Added Kill ID %s on %s with %s involved from ESI" % (
            km.id,
            km.date.strftime("%d/%m/%Y %H:%M"),
            len(attackers)
        )
    )

    return km


@app.task(name="parse_crest", queue="low")
def parse_crest(json, keyhash=None):
    parse_esi(keyhash=keyhash)


@app.task(name="spawn_price_updates", queue="control")
def spawn_price_updates(inline=False):
    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    id_chunks = chunks(
        list(
            Type.objects.filter(
                published=True,
                market_group__isnull=False
            ).values_list(
                'id',
                flat=True
            )
        ),
        500
    )

    for chunk in id_chunks:
        if inline:
            update_prices(chunk)
        else:
            update_prices.delay(chunk)
    print("Queued price updates")


@app.task(name="update_prices", queue="high")
def update_prices(item_ids):
    r = requests.get(
        "https://market.fuzzwork.co.uk/aggregates/",
        params={
            "region": 10000002,
            "types": ",".join(map(str, item_ids))
        }
    ).json()

    with transaction.atomic():
        for key in r.keys():
            item = r[key]
            db_type = Type.objects.get(id=int(key))
            db_type.buy = item['buy']['percentile']
            db_type.sell = item['sell']['percentile']
            db_type.save()

    print(
        "Price updates completed for %s:%s" % (
            item_ids[0],
            item_ids[-1]
        )
    )