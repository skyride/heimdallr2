import ujson
from base64 import b64decode

from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from core.models import Killmail, Involved


def search(request, data):
    data = ujson.loads(b64decode(data))
    
    # Build query
    query = Q()

    # Victim
    if ("victimCharacter" or "victimCorporation" or "victimAlliance") in data:
        search = Q()
        if "victimCharacter" in data:
            search.add(Q(involved__character_id__in=data['victimCharacter']), Q.OR)
        if "victimCorporation" in data:
            search.add(Q(involved__character_id__in=data['victimCorporation']), Q.OR)
        if "victimAlliance" in data:
            search.add(Q(involved__character_id__in=data['victimAlliance']), Q.OR)
        query.add(search, Q.AND)

    kms = Killmail.objects.filter(
        Q(query)
    ).prefetch_related(
        'ship',
        'system',
        'system__region'
    ).order_by(
        '-date'
    )[:50]

    return HttpResponse(generate_json(kms), content_type="application/json")



def generate_json(kms):
    out = []

    for km in kms:
        o = {
            "id": km.id,
            "date": km.date.strftime("%Y-%m-%d %H:%m"),
            "value": km.value,
            "ship_id": km.ship_id,
            "ship_name": km.ship.name,
            "system_id": km.system_id,
            "system_name": km.system.name,
            "system_sec": km.system.security,
            "region_id": km.system.region_id,
            "region_name": km.system.region.name,
            "attackers": 1,
        }
        print(o['id'], km.date)

        final_blow = Involved.objects.filter(kill_id=km.id, final_blow=True).values(
            'character_id',
            'character__name',
            'corporation_id',
            'corporation__name',
            'alliance_id',
            'alliance__name'
        ).first()
        if final_blow != None:
            final_blow_out = {}

            if "corporation_id" in final_blow:
                final_blow_out.update({
                    "corporation_id": final_blow['corporation_id'],
                    "corporation_name": final_blow['corporation__name']
                })
            if "alliance_id" in final_blow:
                final_blow_out.update({
                    "alliance_id": final_blow['alliance_id'],
                    "alliance_name": final_blow['alliance__name']
                })
            if "character_id" in final_blow:
                final_blow_out.update({
                    "character_id": final_blow['character_id'],
                    "character_name": final_blow['character__name']
                })
            o.update({
                "final_blow": final_blow_out
            })

        victim = Involved.objects.filter(kill_id=km.id, attacker=False).values(
            'character_id',
            'character__name',
            'corporation_id',
            'corporation__name',
            'alliance_id',
            'alliance__name'
        ).first()
        if victim != None:
            victim_out = {}

            if "corporation_id" in victim:
                victim_out.update({
                    "corporation_id": victim['corporation_id'],
                    "corporation_name": victim['corporation__name']
                })
            if "alliance_id" in victim:
                victim_out.update({
                    "alliance_id": victim['alliance_id'],
                    "alliance_name": victim['alliance__name']
                })
            if "character_id" in victim:
                victim_out.update({
                    "character_id": victim['character_id'],
                    "character_name": victim['character__name']
                })
            o.update({
                "victim": victim_out
            })

        out.append(o)

    return ujson.dumps(out)