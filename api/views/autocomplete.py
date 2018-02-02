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

# Player Entities
def autocomplete_character(request, name):
    return _autocomplete(request, name, Character, "involved")

def autocomplete_corporation(request, name):
    return _autocomplete(request, name, Corporation, "involved")

def autocomplete_alliance(request, name):
    return _autocomplete(request ,name, Alliance, "involved")

# Map Entities
def autocomplete_system(request, name):
    return _autocomplete(request, name, System, "kills", ["region__name"], min_length=0)

def autocomplete_constellation(request, name):
    return _autocomplete(request, name, Constellation, "systems__kills", ["region__name"], min_length=0)

def autocomplete_region(request, name):
    return _autocomplete(request, name, Region, "systems__kills", min_length=0)

# SDE Entities
def autocomplete_ship(request, name):
    extra_filters = {
        "group__category_id__in": [6, 65],
        "published": True
    }
    return _autocomplete(request, name, Type, "involved_ship", ["group__name"], extra_filters, min_length=0)

def autocomplete_item(request, name):
    extra_filters = {
        "market_group__isnull": False,
        "published": True
    }
    return _autocomplete(request, name, Type, extra_values=["group__name"], min_length=1)


def _autocomplete(request, name, Model, order_key=None, extra_values=[], extra_filters={}, min_length=3):
    if len(name) >= min_length:
        out = Model.objects.filter(
            name__istartswith=name,
            **extra_filters
        ).values(
            'id',
            'name',
            *extra_values
        )

        if order_key != None:
            out = out.annotate(
                order_key=Count(order_key)
            ).order_by(
                '-order_key'
            )

        return HttpResponse(ujson.dumps(list(out)), content_type="application/json")
    else:
        return JsonResponse(TOO_SHORT_ERROR, status=400)
