import ujson

from django.db.models import Count
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from core.models import Character, Corporation, Alliance, Killmail
from sde.models import System, Constellation, Region, Type

TOO_SHORT_ERROR = {
    "error": "TOO_SHORT",
    "message": "You must provide a search term at least 3 characters long"
}


def autocomplete_character(request, name):
    return _autocomplete(request, name, Character, "involved")

def autocomplete_corporation(request, name):
    return _autocomplete(request, name, Corporation, "involved")

def autocomplete_alliance(request, name):
    return _autocomplete(request ,name, Alliance, "involved")

def autocomplete_system(request, name):
    return _autocomplete(request, name, System, "kills", ["region__name"])

def autocomplete_constellation(request, name):
    return _autocomplete(request, name, Constellation, "systems__kills", ["region__name"])

def autocomplete_region(request, name):
    return _autocomplete(request, name, Region, "systems__kills", min_length=0)


def _autocomplete(request, name, Model, count, extra_values=[], min_length=3):
    if len(name) >= min_length:
        out = Model.objects.filter(
            name__istartswith=name
        ).annotate(
            order_key=Count(count)
        ).order_by(
            '-order_key'
        ).values(
            'id',
            'name',
            *extra_values
        )

        return HttpResponse(ujson.dumps(list(out)), content_type="application/json")
    else:
        return JsonResponse(TOO_SHORT_ERROR, status=400)
