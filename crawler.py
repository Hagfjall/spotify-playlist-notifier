import datetime
from peewee import OP
from database import Track, Tracksinplaylist

OP['MOD'] = 'mod'
__author__ = "Wycheproof"
import database
import spotipy

# sys.stdout = open('log.txt', 'w')
token = database.get_access_token()
sp = spotipy.Spotify(auth=token)

def _analyze_tracks(results,tracks_db,playlist_number):
    for i in results:
            track = i['track']
            try:
                added_by = i['added_by']['id']
                display_name = database.get_display_name(added_by)
                if display_name is None:
                    display_name = sp.user(added_by)['display_name']
                    database.insert_display_name(added_by,display_name)
            except TypeError:
                added_by = ""
            for db_track in tracks_db[:]:
                if db_track.trackId.trackId == track['id'] and \
                                db_track.dateAdded == datetime.datetime.strptime(i['added_at'],
                                                                                 '%Y-%m-%dT%H:%M:%SZ') and \
                                db_track.added_by == added_by:
                    tracks_db.remove(db_track)
                    break
            try:
                db_track = Track.get(Track.trackId == track['id'])
                if db_track.popularity != track['popularity']:
                    db_track.popularity = track['popularity']
                    db_track.save()
                    # print("\tgot track from DB!")
                    # print(db_track.trackId)
                    # print(db_track.duration)
                    # print(db_track.popularity)

            except Track.DoesNotExist:
                # print("\t_No_ track in DB!")
                # print(track['id'])
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
                Tracksinplaylist.get(playlistNumber=playlist_number,
                                     dateAdded=datetime.datetime.strptime(i['added_at'], '%Y-%m-%dT%H:%M:%SZ'),
                                     trackId=db_track,
                                     added_by=added_by)
            except Tracksinplaylist.DoesNotExist:
                Tracksinplaylist.create(playlistNumber=playlist_number,
                                        dateAdded=datetime.datetime.strptime(i['added_at'], '%Y-%m-%dT%H:%M:%SZ'),
                                        trackId=db_track,
                                        added_by=added_by)
                print("created Tracksinplaylist")

def update_playlist_info():
    playlists = database.get_playlists_updated_older_than(days=1)
    print("number of playlists " + str(playlists.count()))
    for playlist in playlists:
        print("\tNew playlist! " + playlist.playlistId + " = '" + playlist.title + "'")
        results = sp.user_playlist(playlist.userId, playlist.playlistId, fields="")
        query = database.get_current_tracks_in_playlist(playlist.number)
        tracks_db = list()
        # it would be much more neat if I was able to solve the SQL query to only get results form the DB
        # with Tracks not listed from spotify API, as: select ... where trackId NOT IN ([all values from spotify api])
        # and dateAdded NOT IN ([all values from spotify API])
        for track in query:
            tracks_db.append(track)
        snapshotId = results['snapshot_id']
        if (snapshotId == playlist.snapshotId):
            # print(results['name'] + " = " + results['id'])
            # print('SNAPSHOT-EQUALS, NO NEED TO CHECK FURTHER')
            database.set_playlist_updated(playlist)
            continue
        else:
            playlist.snapshotId = snapshotId
            database.set_playlist_updated(playlist)
        print("\tNumber of songs in playlist: " + str(results['tracks']['total']))
        print("first run...")
        tracks = results['tracks']
        _analyze_tracks(tracks['items'],tracks_db,playlist.number)
        while tracks['next']:
            print("Run again...")
            tracks = sp.next(tracks)
            _analyze_tracks(tracks['items'],tracks_db,playlist.number)
        database.set_playlist_updated(playlist)
        for track in tracks_db:
            print(track.trackId.trackId + " " + str(track.dateAdded))
            database.set_track_in_playlist_removed(track)

update_playlist_info()