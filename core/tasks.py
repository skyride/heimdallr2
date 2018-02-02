from datetime import datetime

import ujson
import requests

from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware

from heimdallr.celery import app
from core.helpers import parse_crest_date
from core.models import Killmail, Involved, Item, Character, Corporation, Alliance
from sde.models import System, Type





@app.task(name="fetch_character_kills")
def fetch_character_kills(id):
    char = Character.get_or_create(id)
    url = "https://zkillboard.com/api/characterID/%s/page/%s/"
    _fetch_kills(char, url)


@app.task(name="fetch_corporation_kills")
def fetch_corporation_kills(id):
    corp = Corporation.get_or_create(id)
    url = "https://zkillboard.com/api/corporationID/%s/page/%s/"
    _fetch_kills(corp, url)


@app.task(name="fetch_alliance_kills")
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
        source_id=1,
        date=parse_datetime(killmail['killmail_time']),
        system_id=killmail['solar_system_id'],
        ship_id=victim['ship_type_id'],
        value=zkb['totalValue'],
        damage=victim['damage_taken']
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
        "Added Kill ID %s with %s attackers from Redisq" % (
            km.id,
            len(attackers)
        )
    )


@app.task(name="parse_zkill_api")
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
        "Added Kill ID %s on %s with %s attackers from zkill API" % (
            km.id,
            km.date.strftime("%d/%m/%Y %H:%M"),
            len(attackers)
        )
    )


@app.task(name="parse_crest")
def parse_crest(json, keyhash=None):
    if keyhash == None:
        package = ujson.loads(json)
        if Killmail.objects.filter(id=package['killID']).count() > 0:
            print("Kill ID %s already exists" % package['killID'])
            return
    else:
        package = requests.get("https://crest-tq.eveonline.com/killmails/%s/%s/" % (keyhash[0], keyhash[1])).json()
    victim = package['victim']

    # Populate killmail
    km = Killmail(
        id=package['killID'],
        source_id=4,
        date=parse_crest_date(package['killTime']),
        system_id=package['solarSystem']['id'],
        ship_id=victim['shipType']['id'],
        value=0,
        damage=victim['damageTaken']
    )

    if "position" in victim:
        if "x" in victim['position']:
            km.x = victim['position']['x']
            km.y = victim['position']['y']
            km.z = victim['position']['z']

    if "character" in victim:
        km.character = Character.get_or_create(victim['character']['id'])
    if "corporation" in victim:
        km.corporation = Corporation.get_or_create(victim['corporation']['id'])
    if "alliance" in victim:
        km.alliance = Alliance.get_or_create(victim['alliance']['id'])

    km.save()

    # Populate attackers
    attackers = []
    for attacker in package['attackers']:
        a = Attacker(
            kill=km,
            damage=attacker['damageDone']
        )

        if "final_blow" in attacker:
            a.final_blow = attacker['finalBlow']
        if "character" in attacker:
            a.character = Character.get_or_create(attacker['character']['id'])
        if "corporation" in attacker:
            a.corporation = Corporation.get_or_create(attacker['corporation']['id'])
        if "alliance" in attacker:
            a.alliance = Alliance.get_or_create(attacker['alliance']['id'])

        if "shipType" in attacker:
            a.ship_id = attacker['shipType']['id']
        if "weaponType" in attacker:
            a.weapon_id = attacker['weaponType']['id']
        #a.save()
        attackers.append(a)
    Attacker.objects.bulk_create(attackers)

    # Populate Items
    items = []
    for item in victim['items']:
        i = Item(
            kill=km,
            type_id=item['itemType']['id'],
            singleton=item['singleton'],
            flag=item['flag']
        )

        if "quantityDropped" in item:
            i.quantity = item['quantityDropped']
        if "quantityDestroyed" in item:
            i.quantity = item['quantityDestroyed']
        #i.save()
        items.append(i)
    Item.objects.bulk_create(items)

    print(
        "Added Kill ID %s on %s with %s attackers from CREST" % (
            km.id,
            km.date.strftime("%d/%m/%Y %H:%M"),
            len(attackers)
        )
    )


@app.task(name="spawn_price_updates")
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


@app.task(name="update_prices")
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