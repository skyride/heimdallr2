import ujson
from base64 import b64decode

from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from core.models import Killmail


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
        query
    ).annotate(
        involved_count=Count('involved')
    ).order_by(
        '-date'
    )[:10]

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
            "attackers": km.involved_count - 1,
            
        }
        out.append(o)

    return ujson.dumps(out)