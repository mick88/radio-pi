import logging

import mpd
from django.apps import apps
from django.contrib.sites.models import Site
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse

from play_pi.models import Track, RadioStation

logger = logging.getLogger(__name__)

client = mpd.MPDClient()
client.connect("localhost", 6600)


def get_gplay_url(stream_id):
    app = apps.get_app_config('play_pi')
    api = app.get_api()
    return api.get_stream_url(stream_id, app.get_credentials().device_id)


def mpd_play(tracks):
    client = get_client()
    success = False
    site = Site.objects.get_current()
    while not success:
        try:
            client.clear()
            for track in tracks:
                track.mpd_id = client.addid(site.domain + reverse('get_stream', args=[track.id, ]))
                track.save()
            client.play()
            success = True
        except:
            pass


def get_client():
    global client
    try:
        client.status()
    except:
        try:
            client.connect("localhost", 6600)
        except Exception, e:
            logger.error(e.message)
    return client


def mpd_play_radio(station):
    client = get_client()
    client.clear()
    mpd_id = client.addid(station.url)
    station.mpd_id = mpd_id
    station.save()
    client.play()


def get_currently_playing_track():
    status = get_client().status()
    try:
        mpd_id = int(status['songid'])
    except:
        return {}

    if mpd_id == 0:
        return {}

    try:
        track = Track.objects.get(mpd_id=mpd_id)
        return track
    except Track.DoesNotExist:
        try:
            return RadioStation.objects.get(mpd_id=mpd_id)
        except RadioStation.DoesNotExist:
            return {}
    except MultipleObjectsReturned:
        return {}
