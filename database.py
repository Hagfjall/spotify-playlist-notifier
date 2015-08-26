#!/usr/bin/python
from __future__ import print_function
from datetime import datetime
from dateutil.relativedelta import relativedelta
import base64
import os
from peewee import RawQuery
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
    lastChanged = DateTimeField(db_column='lastChanged')
    number = PrimaryKeyField()
    playlistId = CharField(db_column='playlistId')
    snapshotId = CharField(db_column='snapshotId', null=True)
    title = CharField(null=True)
    userId = CharField(db_column='userId')

    class Meta:
        db_table = 'Playlist'


class Track(BaseModel):
    title = CharField()
    artists = CharField()
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


class Subscriber(BaseModel):
    email = CharField()
    lastNotified = DateTimeField(db_column='lastNotified', null=True)
    playlistNumber = ForeignKeyField(db_column='playlistNumber', rel_model=Playlist, to_field='number')

    class Meta:
        db_table = 'Subscriber'
        primary_key = CompositeKey('email', 'playlistNumber')

class SpotifyId(BaseModel):
    displayName = CharField(db_column='displayName')
    id = CharField(primary_key=True)

    class Meta:
        db_table = 'SpotifyId'


def _refresh_access_token(refresh_token):
    payload = {"refresh_token": refresh_token,
               "grant_type": "refresh_token"}
    auth_header = base64.b64encode(client_id + ":" + client_secret)
    headers = {"Authorization": "Basic %s" % auth_header}

    response = requests.post(OAUTH_TOKEN_URL, data=payload,
                             headers=headers)
    if response.status_code != 200:
        print("warning: got errorcode " + response.status_code)
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


def get_unnotified_subscribers():
    return Subscriber.select(Subscriber, Playlist).join(Playlist).where(Subscriber.lastNotified < Playlist.lastChanged)

def get_display_name(spotifyId):
    try:
        return SpotifyId.get(SpotifyId.id == spotifyId)
    except SpotifyId.DoesNotExist:
        return None

def insert_display_name(spotifyId, display_name):
    SpotifyId.create(id=spotifyId,displayName=display_name)

def set_subscriber_notified(subscriber):
    subscriber.lastNotified = datetime.now()
    subscriber.save()
    print("Subscriber updated!")


def get_playlists_updated_older_than(days):
    return Playlist.select().where(Playlist.lastUpdated.between(datetime(year=2000, month=1, day=1),
                                                                datetime.today() - relativedelta(days=days)))


def get_playlist(playlistId):
    return Playlist.get(Playlist.playlistId == playlistId)


def get_current_tracks_in_playlist(playlist_number):
    return Tracksinplaylist.select().join(Track).where((Tracksinplaylist.playlistNumber == playlist_number) &
                                                       (Tracksinplaylist.dateRemoved >> None))


def set_playlist_updated(playlist):
    playlist.lastUpdated = datetime.now()
    playlist.lastChanged = get_latest_change_date(playlist.number)
    playlist.save()


def set_track_in_playlist_removed(track_in_playlist):
    print("Adding remove-date for " + track_in_playlist.trackId.trackId +
          " " + str(track_in_playlist.dateAdded))
    track_in_playlist.dateRemoved = datetime.now().date()
    track_in_playlist.save()


def get_latest_change_date(playlist_number):
    rq = RawQuery(Tracksinplaylist, "SELECT GREATEST(IFNULL(t.c1,0),IFNULL(t.c2,0)) dateAdded "
                                    "FROM (SELECT MAX(dateAdded) c1, MAX(dateRemoved) c2 "
                                    "FROM TracksInPlaylist WHERE playlistNumber=%s) AS t",
                  playlist_number)
    for obj in rq.execute():
        return obj.dateAdded


def get_removed_or_added_tracks_in_playlist(playlistNumber, date):
    return Tracksinplaylist.select().where(
        (Tracksinplaylist.playlistNumber == playlistNumber) & ((Tracksinplaylist.dateAdded > date) |
                                                               (Tracksinplaylist.dateRemoved > date.date())))
