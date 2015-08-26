# spotify-playlist-notifier
Back end for crawling and notifying a subscriber for changes in a certain playlist on spotify. 
Note, this will not allow any input from the user in order to add a playlist/email to the databases. 

Uses [spotipy](https://github.com/plamere/spotipy) for handling the spotify API, [peewee](http://docs.peewee-orm.com/en/latest/) for the database ORM and [sendgrid](https://github.com/sendgrid/sendgrid-python) to handle the email delivery. 
