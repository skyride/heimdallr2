import ujson
from base64 import b64decode

from django.db.models import Q
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
    ).order_by(
        '-date'
    )[:10]

    return HttpResponse(generate_json(kms), content_type="application/json")



def generate_json(kms):
    out = []
    for km in kms:
        out.append({
            "id": km.id,
            "date": km.date
        })

    return ujson.dumps(out)