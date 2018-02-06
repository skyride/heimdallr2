from datetime import datetime

from django.utils.timezone import make_aware


def parse_crest_date(text):
    date, time = text.split(" ")
    years, months, days = date.split(".")
    hours, minutes, seconds = time.split(":")

    return make_aware(
        datetime(
            int(years),
            int(months),
            int(days),
            int(hours),
            int(minutes)
        )
    )
