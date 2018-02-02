import ujson

from django.db.models import Count
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from core.models import Character, Corporation, Alliance, Type, System, Killmail


def autocomplete_character(request, name):
    return _autocomplete_playerentity(request, name, Character)


def autocomplete_corporation(request, name):
    return _autocomplete_playerentity(request, name, Corporation)


def autocomplete_alliance(request, name):
    return _autocomplete_playerentity(request ,name, Alliance)


def _autocomplete_playerentity(request, name, Model):
    if len(name) > 2:
        out = Model.objects.filter(
            name__istartswith=name
        ).annotate(
            kills=Count('involved')
        ).order_by(
            '-kills'
        ).values(
            'id',
            'name'
        )

        return HttpResponse(ujson.dumps(list(out)), content_type="application/json")
    else:
        TOO_SHORT_ERROR = {
            "error": "TOO_SHORT",
            "message": "You must provide a search term at least 3 characters long"
        }
        return JsonResponse(TOO_SHORT_ERROR, status=400)