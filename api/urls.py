"""heimdallr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import re_path

from . import views

urlpatterns = [
    # Autocomplete
    re_path(r'autocomplete/character/(.+)', views.autocomplete_character, name="autocomplete_character"),
    re_path(r'autocomplete/corporation/(.+)', views.autocomplete_corporation, name="autocomplete_corporation"),
    re_path(r'autocomplete/alliance/(.+)', views.autocomplete_alliance, name="autocomplete_alliance"),
    re_path(r'autocomplete/system/(.+)', views.autocomplete_system, name="autocomplete_system"),
    re_path(r'autocomplete/constellation/(.+)', views.autocomplete_constellation, name="autocomplete_constellation"),
    re_path(r'autocomplete/region/(.*)', views.autocomplete_region, name="autocomplete_region"),
    re_path(r'autocomplete/ship/(.*)', views.autocomplete_ship, name="autocomplete_ship"),
]
