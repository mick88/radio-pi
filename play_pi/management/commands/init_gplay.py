from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.apps import apps
from play_pi.models import *


class Command(BaseCommand):
    help = 'Initializes the database with your Google Music library'

    def delete_entries(self):
        self.stdout.write('Clearing DB... ', ending='')
        cursor = connection.cursor()
        # This can take a long time using ORM commands on the Pi, so lets Truncate
        cursor.execute('DELETE FROM ' + Track._meta.db_table)
        cursor.execute('DELETE FROM ' + Album._meta.db_table)
        cursor.execute('DELETE FROM ' + Artist._meta.db_table)
        cursor.execute('DELETE FROM ' + Playlist._meta.db_table)
        cursor.execute('DELETE FROM ' + PlaylistConnection._meta.db_table)
        self.stdout.write('done')

    def import_tracks(self, library):
        # Easier to keep track of who we've seen like this...
        artists = set()
        albums = set()
        count = len(library)
        self.stdout.write('Downloading {} tracks...'.format(count))
        i = 0
        created_tracks = []
        for song in library:
            i += 1

            artist_name = song['artist'] or song['albumArtist'] or "Unknown Artist"

            if artist_name not in artists:
                try:
                    art_url = song['artistArtRef'][0]['url']
                except:
                    art_url = ''
                artist = Artist.objects.create(
                    name=artist_name,
                    art_url=art_url,
                )

                artists.add(artist_name)
            else:
                artist = Artist.objects.get(name=artist_name)

            album_name = song['album']
            if (album_name, artist_name) not in albums:
                try:
                    art_url = song['albumArtRef'][0]['url']
                except:
                    art_url = ''
                album = Album(
                    name=album_name,
                    artist=artist,
                    year=song.get('year', 0),
                    art_url=art_url,
                )

                album.save()
                albums.add((album_name, artist_name))
            else:
                album = Album.objects.get(name=album_name, artist=artist)

            track = Track(
                artist=artist,
                album=album,
                name=song['title'],
                stream_id=song['id'],
                track_no=song.get('trackNumber', 0)
            )
            created_tracks.append(track)
            self.stdout.write(u'{}/{} tracks saved'.format(i, count), ending='\r')
            # self.stdout.write(u'{}/{} tracks saved'.format(i, count), ending='\r')
        self.stdout.write('')
        Track.objects.bulk_create(created_tracks)
        return created_tracks

    def import_playlists(self, playlists):
        self.stdout.write('Importing Playlists...', ending='')
        for playlist in playlists:
            p = Playlist.objects.create(
                pid=playlist['id'],
                name=playlist['name'],
            )
            connections = []
            for entry in playlist['tracks']:
                try:
                    track = Track.objects.get(stream_id=entry['trackId'])
                    playlist_connection = PlaylistConnection(
                        playlist=p,
                        track=track,
                    )
                    connections.append(playlist_connection)
                except Exception as e:
                    self.stderr.write(e.message)

            PlaylistConnection.objects.bulk_create(connections)
        self.stdout.write('done')

    @transaction.atomic()
    def handle(self, *args, **options):
        app = apps.get_app_config('play_pi')
        api = app.get_api()

        self.stdout.write('Connected to Google Music, downloading data...', ending='')
        songs = api.get_all_songs()
        playlists = api.get_all_user_playlist_contents()
        self.stdout.write('done')

        self.delete_entries()
        self.import_tracks(songs)
        self.import_playlists(playlists)



