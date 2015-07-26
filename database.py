#!/usr/bin/python
import datetime
import peewee
from peewee import *

db = MySQLDatabase('spotifyCrawler', unix_socket="/var/run/mysqld/mysqld.sock", read_default_file="my.cnf")

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = db

class Playlist(BaseModel):
    lastUpdated = DateTimeField(db_column='lastUpdated', null=True)
    number = PrimaryKeyField()
    playlistId = CharField(db_column='playlistId')
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
    dateAdded = DateTimeField(db_column='dateAdded')
    dateRemoved = DateTimeField(db_column='dateRemoved', null=True)
    playlistNumber = ForeignKeyField(db_column='playlistNumber', rel_model=Playlist, to_field='number')
    trackId = ForeignKeyField(db_column='trackId', rel_model=Track, to_field='trackId')

    class Meta:
        db_table = 'TracksInPlaylist'
        primary_key = CompositeKey('dateAdded', 'playlistNumber', 'trackId')

query = Playlist.select().where(Playlist.lastUpdated.between(datetime.date.min, datetime.date.today() - datetime.timedelta(days=2)))
#query = Playlist.select().where(Playlist.number == 1)
for playlist in query:
     print playlist.playlistId
#nbr = Playlist.get(Playlist.number == 1)
#print nbr
