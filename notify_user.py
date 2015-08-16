#!/usr/bin/python
import os
import pprint
import sendgrid
import database
SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']

sg = sendgrid.SendGridClient(SENDGRID_API_KEY, raise_errors=True)

message = sendgrid.Mail()
message.add_to(['Example Dude <camilla_wedenstam@hotmail.com>', 'hagfjall@gmail.com'])
message.add_to_name('Example Dude')
message.set_from('bajskorvan@email.com')
message.set_subject('Example')
message.set_text('Konstigt mail va?')
status, msg = sg.send(message)
pprint.pprint(status)
pprint.pprint(msg)

def _notify_users():
    subscribers = database.get_unnotified_subscribers()