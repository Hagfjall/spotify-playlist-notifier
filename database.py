#!/usr/bin/python
from __future__ import print_function
from datetime import datetime
from dateutil.relativedelta import relativedelta
import base64
import os
import requests

from peewee import *

db = MySQLDatabase('spotifyCrawler', unix_socket="/var/run/mysqld/mysqld.sock", read_default_file="my.cnf")
LOCAL_USER = 1
client_id = os.environ["SPOTIFY_CLIENT_ID"]
client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]
OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"


class UnknownField(object):
    pass


class BaseModel(Model):
    class Meta:
        database = db


class Oauth(BaseModel):
    accessToken = CharField(db_column='accessToken', null=True)
    refreshToken = CharField(db_column='refreshToken', null=True)
    id = PrimaryKeyField()
    expires = DateTimeField(db_column='expires')

    class Meta:
        db_table = 'OAuth'


class Playlist(BaseModel):
    lastUpdated = DateTimeField(db_column='lastUpdated', null=True)
    number = PrimaryKeyField()
    playlistId = CharField(db_column='playlistId')
    snapshotId = CharField(db_column='snapshotId', null=True)
    title = CharField(null=True)
    userId = CharField(db_column='userId')

    class Meta:
        db_table = 'Playlist'


class Track(BaseModel):
    duration = IntegerField()
    popularity = IntegerField()
    trackId = CharField(db_column='trackId', primary_key=True)

    class Meta:
        db_table = 'Track'


class Tracksinplaylist(BaseModel):
    added_by = CharField(db_column='addedBy')
    dateAdded = DateTimeField(db_column='dateAdded')
    dateRemoved = DateField(db_column='dateRemoved', null=True)
    playlistNumber = ForeignKeyField(db_column='playlistNumber', rel_model=Playlist, to_field='number')
    trackId = ForeignKeyField(db_column='trackId', rel_model=Track, to_field='trackId')

    class Meta:
        db_table = 'TracksInPlaylist'
        primary_key = CompositeKey('added_by', 'dateAdded', 'playlistNumber', 'trackId')


def _refresh_access_token(refresh_token):
    payload = {"refresh_token": refresh_token,
               "grant_type": "refresh_token"}
    auth_header = base64.b64encode(client_id + ":" + client_secret)
    headers = {"Authorization": "Basic %s" % auth_header}

    response = requests.post(OAUTH_TOKEN_URL, data=payload,
                             headers=headers)
    if response.status_code != 200:
        print("warning: got errorcode " + response.status_code, file=sys.stderr)
        return None
    token_info = response.json()
    if not "refresh_token" in token_info:
        token_info["refresh_token"] = refresh_token
    return token_info


def get_access_token(id=LOCAL_USER):
    response = Oauth.get(Oauth.id == id)
    now = datetime.now() + relativedelta(minutes=10)
    expires = response.expires;
    if now > expires:
        token_info = _refresh_access_token(response.refreshToken)
        response.accessToken = token_info['access_token']
        response.expires = datetime.now() + relativedelta(seconds=token_info['expires_in'])
        response.save()  # Saves to the database
    return response.accessToken


def get_refresh_token(id=LOCAL_USER):
    return Oauth.get(Oauth.id == id).refreshToken


def get_playlists_updated_older_than(days):
    return Playlist.select().where(Playlist.lastUpdated.between(datetime(year=2000, month=1, day=1),
                                                                datetime.today() - relativedelta(days=days)))


def get_playlist(playlistId):
    return Playlist.get(Playlist.playlistId == playlistId)


def get_current_tracks_in_playlist(playlist):
    return Tracksinplaylist.select().where((Tracksinplaylist.playlistNumber == playlist) &
                                           (Tracksinplaylist.dateRemoved >> None))

def set_playlist_updated(playlist):
    playlist.lastUpdated=datetime.now()
    playlist.save()

