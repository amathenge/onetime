from flask import g
import sqlite3
import math, random
from datetime import datetime, timedelta

def connect_db():
    db = sqlite3.connect('onetime.db')
    db.row_factory = sqlite3.Row
    return db

def get_db():
    if not hasattr(g, 'onetime_db'):
        g.onetime_db = connect_db()
    return g.onetime_db

# create a one-time six-digit code (all numbers) randomly.
def onetime():
    # create a list of the digits we need
    digits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    output = ""
    # pick six digits at random from the list and return those.
    # use random.random() to get a random number from 0 - 1
    # multiply by 10 to get an integer from 0 - 10
    # use math.floor() to get the integer (0 - 9)
    # use str() to change that to a string.
    for digit in range(6):
        index = math.floor(random.random() * 10)
        output += str(digits[index])

    return output

# function to return True or False if elapsed time is greater than wait_time minutes.
def otp_ontime(send_time, receive_time, wait_time):
    # send_time and receive_time are datetime objects - but send_time came from the database so it needs
    # to be converted. The format of send_time is YYYY-MM-DD HH:MM:SS.sssss so we need to remove
    # the milliseconds.
    ms_offset = send_time.rfind('.')
    send_time = send_time[:ms_offset]
    send_time = datetime.strptime(send_time, '%Y-%m-%d %H:%M:%S')
    diff = receive_time - send_time
    diff = diff.total_seconds() / timedelta(minutes=1).total_seconds()
    diff = math.floor(diff)
    if diff >= wait_time:
        return False

    return True


