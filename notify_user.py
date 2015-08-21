#!/usr/bin/python
import os
from sendgrid import SendGridError, SendGridClientError, SendGridServerError
import sendgrid

import database

SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']

sg = sendgrid.SendGridClient(SENDGRID_API_KEY, raise_errors=True)


def _notify_users():
    subscribers = database.get_unnotified_subscribers()
    for subscriber in subscribers:
        body = "<html>"
        message = sendgrid.Mail()
        message.add_to(subscriber.email)
        message.set_subject(subscriber.playlistNumber.title + " updated!")
        message.set_from("Spotify Notifier <noreply@hagfjall.se>")
        diff = database.get_removed_or_added_tracks_in_playlist(subscriber.playlistNumber, subscriber.lastNotified)
        current_tracks = database.get_current_tracks_in_playlist(subscriber.playlistNumber.number)
        body += str(diff.count()) + " change(s)<br>"
        for track in diff:
            s = ""
            if (track.dateRemoved == None):
                s += "+ "
            else:
                s += "- " + "removed: " + str(track.dateRemoved) + " "
            s += track.trackId.trackId + " " + " added: " + str(track.dateAdded)
            body += s + "<br>"
        body += "Current tracks:<br>"
        for track in current_tracks:
            body += track.trackId.artists + " - " + track.trackId.title + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + str(
                track.trackId.duration) + "ms" + \
                    "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Popularity: " + str(track.trackId.popularity) + "<br>"

        body += "</html>"
        message.set_html(body)
        try:
            status, msg = sg.send(message)
            database.set_subscriber_notified(subscriber)
        except SendGridClientError:
            print(status)
        except SendGridServerError:
            print(status)

        print(body)


_notify_users()
