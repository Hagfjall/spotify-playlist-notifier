__author__ = "Wycheproof"
import pprint
import sys
import database
import os

import spotipy


token = database.getAccessToken()
# print database.getRefreshToken()
print(token)

username = "b210273"
sp = spotipy.Spotify(auth=token)
# sp.refre
sp.trace = True
user = sp.user(username)
pprint.pprint(user)

# print os.environ["SPOTIFY_CLIENT_SECRET"]
