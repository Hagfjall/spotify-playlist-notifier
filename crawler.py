import datetime
import json
from peewee import IntegrityError, OP
from database import Track, Tracksinplaylist

OP['MOD'] = 'mod'

__author__ = "Wycheproof"
import pprint
import sys
import database
import os
import sys
import spotipy

# sys.stdout = open('log.txt', 'w')
token = database.get_access_token()
sp = spotipy.Spotify(auth=token)


# sp.trace = True

def _set_removed_in_database():
    # TODO ta emot listan pa alla nuvarande laatar och jamfor med alla som spotify ger
    return 0


def printVars(object):
    for i in [v for v in dir(object) if not callable(getattr(object, v))]:
        print '\n%s:' % i
        print getattr(object, i)


def _update_playlist_info():
    playlists = database.get_playlists_updated_older_than(days=1)
    print("number of playlists " + str(playlists.count()))
    for playlist in playlists:
        print("\tNew playlist! " + playlist.playlistId + " = '" + playlist.title + "'")
        results = sp.user_playlist(playlist.userId, playlist.playlistId, fields="")
        tracks_db = database.get_current_tracks_in_playlist(playlist.number)
        snapshotId = results['snapshot_id']
        if (snapshotId == playlist.snapshotId):
            # print(results['name'] + " = " + results['id'])
            print('SNAPSHOT-EQUALS, NO NEED TO CHECK FURTHER')
            database.set_playlist_updated(playlist)
            # continue
        else:
            playlist.snapshotId = snapshotId
            playlist.save()
        print("\tNumber of songs in playlist: " + str(len(results['tracks']['items'])))
        # contains trackId,playlistNumber, addedBy, dateAdded
        # songs_in_playlist = list()
        # songs_in_playlist.append(['10ViidwjGLCfVtGPfdcszR'], '2', 'b210273', '2015-08-11 19:10:28')
        for i in results['tracks']['items']:
            track = i['track']
            # songs_in_playlist.append([track['id'],i['added_by']['id'],i['added_at']])
            try:
                db_track = Track.get(Track.trackId == track['id'])
                if (db_track.popularity != track['popularity']) or (db_track.duration != track['duration_ms']):
                    # print("updated something")
                    db_track.popularity = track['popularity']
                    db_track.duration = track['duration_ms']
                    db_track.save()
                # print("\tgot track from DB!")
                print(db_track.trackId)
                # print(db_track.duration)
                # print(db_track.popularity)

            except Track.DoesNotExist:
                # print("\t_No_ track in DB!")
                print(track['id'])
                # print(track['duration_ms'])
                # print(track['popularity'])
                artists = ""
                for c, artist in enumerate(track['artists']):
                    if (c > 0):
                        artists += ", "
                    artists += artist['name']
                db_track = Track.create(trackId=track['id'],
                                        duration=track['duration_ms'],
                                        popularity=track['popularity'],
                                        artists=artists,
                                        title=track['name'])
            try:
                Tracksinplaylist.get(playlistNumber=playlist.number,
                                     dateAdded=datetime.datetime.strptime(i['added_at'], '%Y-%m-%dT%H:%M:%SZ'),
                                     trackId=db_track,
                                     added_by=i['added_by']['id'])
                print("Got Tracksinplaylist")
            except Tracksinplaylist.DoesNotExist:
                Tracksinplaylist.create(playlistNumber=playlist.number,
                                        dateAdded=datetime.datetime.strptime(i['added_at'], '%Y-%m-%dT%H:%M:%SZ'),
                                        trackId=db_track,
                                        added_by=i['added_by']['id'])
                print("created Tracksinplaylist")

                # print("should add a TrackInPlaylist here...")
        database.set_playlist_updated(playlist)
        # print(songs_in_playlist)


_update_playlist_info()
# results = sp.user_playlist('b210273', '1Thv4ABIUMx0GfHbZE4nvk', fields="")
#
# for i in results['tracks']['items']:
#     track = i['track']
#     artists = ""
#     for c, artist in enumerate(track['artists']):
#         if (c > 0):
#             artists += ", "
#         artists += artist['name']
#     print(track['name'] + " - " + artists)



# print(datetime.date.today())
# songs_in_playlist = list()
# songs_in_playlist.append(['10ViidwjGLCfVtGPfdcszR', '2', 'b210273', '2015-08-11 19:10:28'])
# b = Tracksinplaylist.select().where((Tracksinplaylist.trackId.not_in('10ViidwjGLCfVtGPfdcszR')) & (
#                                         Tracksinplaylist.dateAdded.not_in('2015-08-11 19:10:28')))

# Tracksinplaylist.select().where(Tracksinplaylist.not_in(b))
# for c in b:
#     print(c.trackId.trackId)
#     print(c.dateAdded)
# songs_in_playlist.append(['TEST','21','b','19:10:28'])
# songs_in_playlist.append(['AA','11','a','10:10:28'])
# track_ids = [item[0] for item in songs_in_playlist]
# dateAdded = [item[3] for item in songs_in_playlist]
# print(track_ids)
# print(dateAdded)
#
# # (Tracksinplaylist.playlistNumber == 2) &
# #                                 (Tracksinplaylist.dateRemoved >> None) &
# a = Tracksinplaylist.select().where(Tracksinplaylist.trackId.not_in(track_ids) &
#                                      Tracksinplaylist.dateAdded.not_in(dateAdded ))
# pprint.pprint(a)
# #TODO check why I dont get any hit on 10ViidwjGLCfVtGPfdcszR
# for b in a:
#     print(b.trackId.trackId)
