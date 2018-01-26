import requests
import ujson

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from core.tasks import parse_redisq


class Command(BaseCommand):
    help = "Permanently fetches kills from zkill"

    def handle(self, *args, **options):
        while True:
            r = requests.get("https://redisq.zkillboard.com/listen.php")
            if r.status_code == 200:
                r = r.json()
                if r['package'] != None:
                    parse_redisq.delay(ujson.dumps(r))
                    print(
                        "[%s]: Started parse request for kill ID %s" % (
                            now(),
                            r['package']['killID']
                        )
                    )
